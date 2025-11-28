from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser



def call_deepseek_local(prompt_text):
    print("尝试连接本地模型")
    llm = Ollama(
        model="deepseek-r1:1.5b",  # Ollama中的模型名称
        base_url="http://localhost:11434",  # Ollama本地服务地址
        temperature=0,  # 控制随机性，0-1之间，值越高随机性越强
        # num_predict=512,  # 可选：最大生成长度
    )  
    # 创建提示模板
    prompt_template = PromptTemplate(
        input_variables=["input_text"],
        template="请回答以下问题：{input_text}"
    )

    # 创建处理链
    chain = prompt_template | llm | StrOutputParser()

    print("已经连接上本地模型")
    """
    获取模型对输入prompt的响应
    """
    try:
        # 调用模型
        print("尝试调用本地模型")
        response = chain.invoke({"input_text": prompt_text})
        print("AI返回的结果时:",response)
        return response
    except Exception as e:
        print(f"发生错误：{str(e)}")
        return f"发生错误：{str(e)}"
    
def build_prompt(citation: str, origin_query):

    test_prompt = f"""请参考如下内容{citation}给出如下问题的回答{origin_query},如果参考内容为空，请你独立生成结果；如果你不知道结果该如何生成并且参考内容没有帮助请如实回答，
    不要给出编造的内容,务必保持内容的严谨性"""

    return test_prompt


    
def prompt_for_task_distribution(origin_query):

    # 更严格的提示词版本
    STRICT_PROMPT_TEMPLATE = f"""
        你是一个任务调度器。请分析用户输入并返回严格的JSON格式，只包含两个字段：task_type,prod_type。

        输入: {origin_query}

        只返回JSON，不要任何其他文字,并且json的格式必须严格按照如下形式给出：

        JSON格式：
        {{
        "task_type": "任务类型",
        "prod_type": "产品种类"
        }}
        其中task_type只能在["产品市场概览","保险宏观分析"]中选取一种，如果问题更关心商业保险的产品市场 返回"产品市场概览"，如果问题更关心社会保险 返回保险宏观分析；
        prod_type变量默认返回空字符串 当task_type是“产品市场概览”时进一步分析关心的是什么市场，此时prod_type变量仅能在["健康险","人寿保险"，"年金保险"]中选择一种，
        如果task_type是其他内容则prod_type返回空字符串
        请务必记住如果task_type为"产品市场概览" ,请进一步分析prod_type是["健康险","人寿保险"，"年金保险"]中的哪个
        例如：
            示例一：
                问题是：现在的最近商业保险市场上的健康险产品都有哪些
                回答应该是{{
                "task_type": "产品市场概览",
                "prod_type": "健康险"
                }}
            示例二：
                问题是：我国的社会养老保险面临的最大问题是什么
                回答应该是{{
                "task_type": "保险宏观分析",
                "prod_type": ""
                }}    

        """

        
    return STRICT_PROMPT_TEMPLATE

if __name__ == '__main__':
  
    # 测试prompt
    origin_query = ["请解释一下RAg是如何帮助LLM的"]
    print("正在调用模型...")
    result = call_deepseek_local(origin_query)

    print("\n=== 模型响应 ===")
    print(result)
