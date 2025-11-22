import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
# from sklearn.feature_extraction.text import TfidfVectorizer
import chromadb
import os
import re
import pickle

class RAG_database:

    def __init__(self):
        # self.dimension = dimension
        self.embedding_model = ONNXMiniLM_L6_V2()
        pass

    @staticmethod
    def split_chunks_for_any(text, chunk_size = 5000, chunk_overlap=50):
        # 初始化文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )

        # # 待分割的文本
        # with open("long_text_for_test.txt", encoding='utf-8') as f:
        #     text = f.read()

        # 切分文本
        chunks = text_splitter.split_text(text)
        return chunks



    def split_chunks(self, chunk_size = 5000, chunk_overlap=50):
        # 初始化文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )

        # 待分割的文本
        with open("long_text_for_test.txt", encoding='utf-8') as f:
            text = f.read()

        # 切分文本
        chunks = text_splitter.split_text(text)

        self.chunks = chunks

    def vectorize_chunks(self):
        """将切块完成后的文本实现向量化"""

        vectors = np.array(self.embedding_model(self.chunks)).astype(("float32"))

        # 创建FAISS索引
        self.dimension = vectors.shape[1]
        index = faiss.IndexFlatIP(self.dimension)  # 使用内积相似度
        index.add(vectors)

        self.index = index

    def get_citation_for_query(self, query:list[str]):
        """将传入的查询向量化并在文本库里寻找相似的向量,要求传入的是list"""

        query_vector = np.array(self.embedding_model(query)).astype(("float32"))

        # 搜索最相似的3个结果 返回结果中indices是传入的查询数量*3 的形状
        scores, indices = self.index.search(query_vector, 3)

        # 简单起见 默认只传入一个query
        citation_list = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if score > 0.4:
                citation_list.append(self.chunks[idx])
            # print(i)
            # print(score," ",idx)
            #
        #
        # citation_list = [ self.chunks[idx] for idx in indices.flatten() ]

        return citation_list




    def save_to_disk(self, save_path="./faiss_db"):
        os.makedirs(save_path, exist_ok=True)
        
        # 保存FAISS索引
        faiss.write_index(self.index, f"{save_path}/index.faiss")
        
        # 保存文本数据和其他元数据
        with open(f"{save_path}/metadata.pkl", "wb") as f:
            pickle.dump({
                'chunks': self.chunks,
                'dimension': self.dimension
            }, f)


    def load_from_disk(self, save_path="./faiss_db"):
        """从磁盘加载FAISS索引和文本数据"""
        # 加载FAISS索引
        self.index = faiss.read_index(f"{save_path}/index.faiss")
        
        # 加载文本数据
        with open(f"{save_path}/metadata.pkl", "rb") as f:
            metadata = pickle.load(f)
            self.chunks = metadata['chunks']
            self.dimension = metadata['dimension']

def read_and_clean_txt_files():
    """
    读取Comments文件夹中的所有txt文件，删除被<>包裹的HTML标签（包括</p>这样的闭合标签）
    返回清理后的文本列表
    """
    cleaned_texts = []
    comments_dir = "./Comments"
    
    # 检查目录是否存在
    if not os.path.exists(comments_dir):
        print(f"错误：目录 {comments_dir} 不存在")
        return cleaned_texts
    
    # 获取所有txt文件
    txt_files = [f for f in os.listdir(comments_dir) if f.endswith('.txt')]
    print(f"找到 {len(txt_files)} 个txt文件")
    
    # 正则表达式：匹配所有HTML标签，包括闭合标签
    # 这会匹配 <p>, </p>, <div>, </div>, <span class="test"> 等所有HTML标签
    html_tag_pattern = r'<\/?[a-zA-Z][^>]*>'
    
    # 读取并清理每个文件
    for filename in txt_files:
        file_path = os.path.join(comments_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # 删除所有HTML标签（包括闭合标签）
                cleaned_content = re.sub(html_tag_pattern, '', content)
                cleaned_texts.append(cleaned_content)
        except Exception as e:
            print(f"读取文件 {filename} 时出错: {e}")
    
    print(f"成功处理 {len(cleaned_texts)} 个文件")
    return cleaned_texts
 

if __name__ == "__main__":

    # 首先读取txt文件

    rag = RAG_database()
    query = ["长期护理保险的发展趋势"]
    texts = read_and_clean_txt_files()
    print(f"第一个文件的前200个字符: {texts[0][:200] if texts else '无内容'}")

    all_chunks = [chunk  for text in texts for chunk in RAG_database.split_chunks_for_any(text) if len(chunk)>50]

    all_chunks = texts
    print(all_chunks[:5])
    rag.chunks = all_chunks
    # rag.split_chunks()
    print("===========================开始向量化===========================")
    rag.vectorize_chunks()
    rag.save_to_disk("./faiss_db")
    print("===========================向量化完毕===========================")
    print(rag.get_citation_for_query(query))

