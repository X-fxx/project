# -*- encoding: utf-8 -*-
'''
@File        :   gradio.py
@Time        :   2024/07/01 11:19:09
@Author      :   Feng zhixin 
@Description :   prompt界面实现
'''

# here put the import lib

import gradio as gr
from utils import *
import pandas as pd

def script_generation(theme, style, num):
    get_subject_prompt = """你的角色是脚本书写专家，你的任务是帮助用户生成符合要求的脚本。
            约束: 
            1. 如果输入的文本长度超过了上下文的长度限制，请先总结之前读取的内容，再对后面的内容进行分析。
            2. 对输入的主题进行正确的理解。
            3. 输出主题、主要人物、风格、场景与画面、人物表演与对白、备注等字段。
            输出要求:
            1. 不要输出 markdown 格式，不要输出 markdown 格式，不要输出 markdown 格式。
            2. 输出 json 格式。格式请参考输出示例.
            3. 备注：数组，为空可忽略。
            4. 风格：["Comic style", "Realistic style", "Landscape painting style"] 数组，为空可忽略。
            **示例**:
            输入:
            此次脚本的主题为The great wall of china，共需要生成3个画面。
            输出：
            {{"overview":
              {{"主题": "The great wall of china",
              "主要人物": "游客、导游",
              "风格": ["Realistic style"]}}
            "script": [
            {{"序号": "1",
            "场景与画面": "清晨，长城的远景，晨雾弥漫。",
            "人物表演与对白": "旁白:这是世界上最伟大的建筑之一，长城。",
            "备注": ""}},
            {{"序号": "2",
            "场景与画面": "游客们在长城上行走，导游在讲解。",
            "人物表演与对白": "导游: 长城全长超过一万三千英里，横贯中国北部。",
            "备注": ""}},
            {{"序号": "3",
            "场景与画面": "夕阳西下，长城被染成金色。",
            "人物表演与对白":"旁白: 长城不仅是中国的象征，也是全人类的宝贵遗产。",
            "备注": ""}}]}}
            **示例结束**
            请按照上述示例，完成下面内容的输出。
            输入:此次脚本的主题为{theme}, 风格为{style}，共需要生成{num}个画面。
            输出"""
    response = invoke_example_glm3(get_subject_prompt.format(theme=theme, style=style,num=num))   # 生成的画面数越多，需要的时间越长
    # 取出response中输出后面的内容，并转换为字典
    overview, script, data_dict = format_conversion(response)
    # data = pd.DataFrame(response)
    return overview, script, data_dict

def detail_generation(data_dict):
    prompt =  """
            你的角色是脚本润色家, 任务是根据输入的脚本场景, 生成prompt和negative prompt.
            约束：约束是你必须要遵守的规定
            1. prompt中的内容是与脚本场景相关的内容, 必须对人物细节的描述, 对场景细节的描述, 对画质和分辨率的要求；
            2. negative prompt中的内容是与脚本场景不相关的内容, 必须是对人物细节的描述, 是对场景细节的描述, 是对画质和分辨率的要求；
            3. prompt和negative prompt的描述要符合脚本场景的风格
            输出：
            1.不要输出 markdown 格式,不要输出 markdown 格式,不要输出 markdown 格式
            2. 输出 json 格式。格式请参考输出示例。请注意 json 字段的值,换行要用转义字符 \n 表示,不要直接输出换行符
            3. 输出格式要严格按照要求输出, 且必须都为中文
            **示例**
            输入：场景描述为清晨，长城的远景，晨雾弥漫。人物对话为旁白:这是世界上最伟大的建筑之一，长城。
            输出：
            {{'prompt': '高清4K画质,人物穿着为夏天的半袖,场景是中国长城', 'negative_prompt': '模糊,冬天,夜晚'}}
            **示例结束**
            请按照上述要求, 完成下面的输出:
            输入: 场景描述为{sence}, 人物对话为{dialog}
            输出"""
    script = data_dict['script']
    new_data = {"prompt": [], "negative_prompt": []}
    for i in range(len(script)):
        sence = script[i]['场景与画面']
        dialog = script[i]['人物表演与对白']
        all_prompt = prompt.format(sence=sence, dialog=dialog)
        response = invoke_example_glm3(all_prompt)
        print(response)
        data = response.replace(' ', '').replace('\n', '')
        data = json.loads(data)
        new_data['prompt'].append(data["prompt"])
        new_data['negative_prompt'].append(data['negative_prompt'])
    result = pd.DataFrame(new_data) 
    return result
        



block = gr.Blocks().queue()  # 创建一个新的 Gradio 界面实例，并为其添加请求队列功能，以便在处理多个并发请求时能够按顺序进行处理。

with block:
    # --------------------------------- 1. 完成整体的布局结构 -------------------------------- #
    gr.Markdown("# 用户界面")   # gradio显示的文本内容是按照Markdown的形式来实现
    with gr.Row():  
        # 主题输入部分
        theme_input = gr.Textbox(placeholder="Please input the subject.", label="Subject")  # 会直接获取返回的数值

    with gr.Row():
        with gr.Column():
            # 风格选择部分
            style_dropdown = gr.Dropdown(choices=["Comic style", "Relastic style", "Landscape painting style"], label="Style")
        with gr.Column():
            # 画面数量选择部分
            num_dropdown = gr.Dropdown(choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], label="Number of Scenes")
    with gr.Row():
        # 脚本生成按钮
        script_button = gr.Button("Script Generation")
    with gr.Row():
        # 输出表格
        output_text = gr.DataFrame()

    with gr.Row():
        output_table = gr.DataFrame()
    
    with gr.Row():
        detail_prompt = gr.Button("Detailed Prompt")
    
    with gr.Row():
        detail_prompt_text = gr.DataFrame()
        
    # with gr.Row():
    #     # 脚本生成按钮
    #     image_button = gr.Button("Image Generation")
    # with gr.Row():
    #     image_output = gr.Image(label="生成的图片")
    # ---------------------------------------------------------------------------- #

    # ---------------------------------- 2. 设置函数反应 ---------------------------------- #
    data_dict = gr.State()  # 设置临时变量返回
    script_button.click(
        fn=script_generation, 
        inputs=[theme_input, style_dropdown, num_dropdown],   # 变量名的形式按照列表形式传入
        outputs=[output_text, output_table, data_dict]
    )   # output中要提前指定函数返回的位置(即gr中的变量)

    detail_prompt.click(fn=detail_generation, inputs=[data_dict], outputs=[detail_prompt_text])
    # script_button.click(invoke_example_glm3, inputs=[prompt_input, content_input], outputs=script_output)

block.launch(server_name='0.0.0.0')
print("launch success")