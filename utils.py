# -*- encoding: utf-8 -*-
'''
@File        :   utils.py
@Time        :   2024/07/01 12:47:26
@Author      :   Feng zhixin 
@Description :   get the openai response
'''

# here put the import lib
from transformers import AutoTokenizer, AutoModel
import os
import pandas as pd
import json
os.environ["CUDA_VISIBLE_DEVICES"] = "2"
tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True).half().cuda()
model = model.eval()
def invoke_example_glm3(sys_prompt):
    response, history = model.chat(tokenizer, sys_prompt, temperature=0.3)
    data = response.replace(' ', '').split('输出：')[-1]
    data = data.split('示例结束')[0].replace('\n', '')
    import pdb; pdb.set_trace()
    # 如果data可以正确被解析为json，则执行下面的指令；如果报错，则重新生成
    try:
        data_dict = json.loads(data)
    except:
        response = invoke_example_glm3(sys_prompt)
        data = response.replace(' ', '').split('输出：')[-1]
        data = data.split('示例结束')[0].replace('\n', '')
        data_dict = json.loads(data)
    return response

def format_conversion(response):
    # import pdb; pdb.set_trace()
    data = response.replace(' ', '').split('输出：')[-1]
    data = data.split('示例结束')[0].replace('\n', '')
    data_dict = json.loads(data)
    overview = pd.DataFrame(data_dict['overview'])
    script = pd.DataFrame(data_dict['script'])
    return overview, script, data_dict

if __name__ == '__main__':
    text='西游记'
    num=5
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
            输入:此次脚本的主题为{text}, 共需要生成{num}个画面。
            输出"""
            
    get_subject_prompt = get_subject_prompt.format(text=text, num=num)
    print(get_subject_prompt)
    
    # import pdb; pdb.set_trace()
    response = invoke_example_glm3(get_subject_prompt)
    data = format_conversion(response)
    print(response)
    print(data)
