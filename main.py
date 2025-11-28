from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import faiss
import pickle
import  json
import numpy as np
from RAG_DB.RAG_DB import RAG_database
from scrawler.IO_data import get_insurance_data_with_cache
from LLM.Local_LLM import prompt_for_task_distribution, call_deepseek_local
import re

def parse_llm_output(raw_output: str, user_query: str) -> dict:
    """
    解析 LLM 返回内容（可能包含前后多余内容）并补充值类型。
    :param raw_output: LLM 的原始字符串，例如 "json { \"task_type\":... }"
    :param user_query: 用户输入，用于补全产品类型
    """

    # 1. 正则安全提取最外层 JSON
    json_match = re.search(r"\{.*\}", raw_output, flags=re.DOTALL)
    if not json_match:
        return {
            "task_type": "",
            "prod_type": "",
            "error": "No JSON object found in LLM output."
        }

    json_str = json_match.group(0)

    # 2. 尝试解析 JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "task_type": "",
            "prod_type": "",
            "error": "Invalid JSON format in LLM output."
        }

    task_type = data.get("task_type", "")
    prod_type = data.get("prod_type", "")
    print(f"prod_type的返回值是{not prod_type}")
    # 3. 如果缺失产品类别 → 正则从用户 query 补全
    if task_type == "产品市场概览" and not prod_type:
        print("进来了")
        product_map = {
            "健康险": r"(健康险|医疗险|重疾险)",
            "人寿保险": r"(人寿险|寿险|人寿保险)",
            "年金保险": r"(年金险|养老金|年金保险)"
        }

        for key, pattern in product_map.items():
            print(f"此时是{key}")
            if re.search(pattern, user_query, re.IGNORECASE):
                prod_type = key
                break

    return {
        "task_type": task_type,
        "prod_type": prod_type
    }


def task_distribution(Query, output_json:dict):

    if output_json["task_type"] == "产品市场概览":
        return  get_insurance_data_with_cache()
    else :
        return call_deepseek_local(prompt)
    pass

# if __name__ == "__main__":



if __name__ == "__main__":
    Query = "请问最近商业保险市场上的健康险产品有什么更新吗"
    prompt = prompt_for_task_distribution(Query)
    # prompt = prompt_for_task_distribution("请问我国的社会养老保险有什么发展重点")
    # print(prompt)
    # print(json.loads(call_deepseek_local(prompt)))
    print(parse_llm_output(call_deepseek_local(prompt), Query))
    response = parse_llm_output(call_deepseek_local(prompt), Query)
    task_distribution(response)


    