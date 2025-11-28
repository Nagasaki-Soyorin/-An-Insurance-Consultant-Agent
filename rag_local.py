
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
import numpy as np
from RAG_DB.RAG_DB import RAG_database


# 导入本地大模型
from LLM.Local_LLM import call_deepseek_local , build_prompt
# 导入爬虫必要参数
from scrawler.web_params import cookies, headers, json_data



def RAG_main(origin_query : str) -> str:
    
    """集成上述所有RAG功能"""
    """ 输入 query 输出检索到的文章"""
    db2 = RAG_database()
    db2.load_from_disk("./faiss_db")
    vectors = np.array(db2.embedding_model([origin_query])).astype("float32")
    D, I = db2.index.search(vectors, k=3)  # 搜索最相似的10个
    results = [db2.chunks[i] for i in I[0]]
    prompt = build_prompt("======字段分隔符======".join(results), origin_query)
    for idx, comment in enumerate(results):
        print(f"===============第{idx}篇文章================")
        print(comment[:150])
    # 调用本地大模型
    print("=====================高雅人士正在请教DeepSeek====================")
    response = call_deepseek_local(prompt)
    
    return response









if __name__ == "__main__":
# 加载使用
    db2 = RAG_database()
    db2.load_from_disk("./faiss_db")
    # print(len(db2.index))
    origin_query = "如何构建一个有效的巨灾保险制度"
    # 现在可以查询
    vectors = np.array(db2.embedding_model([origin_query])).astype("float32")
    D, I = db2.index.search(vectors, k=3)  # 搜索最相似的10个
    results = [db2.chunks[i] for i in I[0]]
    for  result in results:
        print(result)

    prompt = build_prompt("======字段分隔符======".join(results), origin_query)

    # 调用本地大模型
    print("=====================高雅人士正在请教DeepSeek====================")
    response = call_deepseek_local(prompt)
    print(response)