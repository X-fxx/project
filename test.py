# -*- encoding: utf-8 -*-
'''
@File        :   test.py
@Time        :   2024/07/01 10:32:27
@Author      :   Feng zhixin 
@Description :   使用GLM3输出内容，会调用两次
'''

# here put the import lib

import openai
import json

openai.api_base = "http://localhost:8000/v1"
openai.api_key = "none"

def invoke_example_glm3(prompt, content):

    full_content = prompt.format(content=content)
    response = openai.ChatCompletion.create(
        model="chatglm3-6b",
        messages=[
            {"role": "user", "content": full_content}
        ],
        stream=False,
        top_p=0.7,
        temperature=0
    )
    valid_content = response['choices'][0]['message']['content']
    return valid_content


if __name__ == "__main__":
    json_path = "/home/log_generation/data/filtered_json_output.json"
    with open(json_path, 'r') as f_reader:
        dataset = json.load(f_reader)
    
    output_json = "/home/log_generation/data/translate_cmd.json"
    full_content = '''
    作为一个熟悉Linux指令并能够准确将中文翻译为英文的AI专家，你的任务是判断输入是否符合英文语法，如果符合，则将Linux指令翻译成为简体中文描述；如果不符合，则输出"该内容无法翻译"。
    请确保你提供的翻译逻辑清晰、语句通顺。

    注意：不要将文件名和Linux指令翻译为简体中文，并且删除中文中的引号和句号！！

    示例：

    输入: Take one random word from the /usr/share/dict/words file and rename it to new_[word].
    输出: 从 /usr/share/dict/words 文件中随机取出一个单词并将其重命名为 new_[word]

    输入：Find all files and search for the string \"string\" in them, then list the files that contain the string.
    输出：查找所有文件并在其中搜索字符串string，然后列出包含该字符串的文件

    输入：echo 'Hello world no.' $(shuf -i 1-1000 -n 1) '!'
    输出：该内容无法翻译

    请根据以上说明翻译此输入：{content}
    输出：'''

    # Initialize variables for filtering and renumbering
    trans_dataset = {}
    new_index = 1

    # Filter the dataset based on the 'invocation' string
    for key, value in dataset.items():
        response = invoke_example_glm3(full_content, value["invocation"])
        trans_dataset = {
            'src': response,
            'trg': value['cmd']
        }
        print(trans_dataset)
        # transed_json = open(output_json, 'a', encoding='utf-8')
        transed_json = json.dumps(trans_dataset, ensure_ascii=False)
        with open(output_json, 'a', encoding='utf-8') as output_file:
            output_file.write(transed_json)
            output_file.write("\n")

        

