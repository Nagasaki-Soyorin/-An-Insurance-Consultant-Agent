



import os
import re
import chromadb
from chromadb.config import Settings
import tiktoken
from tqdm import tqdm
import glob

class CommentProcessor:
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text):
        """计算文本的token数量"""
        return len(self.encoding.encode(text))
    
    def remove_html_tags(self, text):
        """删除HTML标签，特别是<p>标签"""
        # 移除<p>和</p>标签
        text = re.sub(r'</?p>', '', text)
        # 可选：移除其他常见的HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    def read_comment_files(self, folder_path):
        """读取Comments文件夹中的所有txt文件"""
        comments = []
        file_paths = []
        
        # 获取所有txt文件
        pattern = os.path.join(folder_path, "*.txt")
        txt_files = glob.glob(pattern)
        
        print(f"找到 {len(txt_files)} 个txt文件")
        
        for file_path in tqdm(txt_files, desc="读取文件"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # 只处理非空文件
                        # 清理HTML标签
                        cleaned_content = self.remove_html_tags(content)
                        comments.append(cleaned_content)
                        file_paths.append(file_path)
            except Exception as e:
                print(f"读取文件 {file_path} 时出错: {e}")
        
        return comments, file_paths
    
    def chunk_text(self, text, chunk_size=500, overlap=100):
        """将文本切分成指定大小的chunk"""
        if not text:
            return []
            
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # 如果已经到达末尾，则退出循环
            if end >= len(tokens):
                break
                
            # 移动起始位置，考虑重叠
            start += chunk_size - overlap
            
        return chunks
    
    def process_all_comments(self, folder_path, chunk_size=500, overlap=100):
        """处理所有评论文件并切分成chunks"""
        print("开始读取和清理评论文件...")
        comments, file_paths = self.read_comment_files(folder_path)
        
        print("开始切分文本...")
        all_chunks = []
        chunk_metadata = []
        chunk_sources = []
        
        for i, (comment, file_path) in tqdm(enumerate(zip(comments, file_paths)), 
                                          total=len(comments), desc="处理评论"):
            chunks = self.chunk_text(comment, chunk_size, overlap)
            
            for j, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                chunk_metadata.append({
                    "file_path": file_path,
                    "chunk_index": j,
                    "total_chunks": len(chunks),
                    "comment_index": i,
                    "tokens": self.count_tokens(chunk)
                })
                chunk_sources.append({
                    "file": os.path.basename(file_path),
                    "chunk": j,
                    "original_file": file_path
                })
        
        print(f"总共生成 {len(all_chunks)} 个chunks")
        return all_chunks, chunk_metadata, chunk_sources

def setup_chromadb():
    """设置ChromaDB客户端和集合"""
    # 创建持久化客户端
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # 获取或创建集合
    collection = client.get_or_create_collection(
        name="comments_collection",
        metadata={"description": "处理后的评论数据chunks"}
    )
    
    return client, collection

def store_in_chromadb(collection, chunks, metadata):
    """将chunks存储到ChromaDB中"""
    print("开始向ChromaDB存储数据...")
    
    # 准备数据
    documents = chunks
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = metadata
    
    # 批量存储（如果数据量很大，可以分批存储）
    batch_size = 100
    for i in tqdm(range(0, len(documents), batch_size), desc="存储到ChromaDB"):
        end_idx = min(i + batch_size, len(documents))
        
        collection.add(
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
    
    print(f"成功存储 {len(documents)} 个文档到ChromaDB")

def main():
    # 初始化处理器
    processor = CommentProcessor()
    
    # 设置ChromaDB
    client, collection = setup_chromadb()
    
    # 处理评论文件
    comments_folder = "./Comments"  # 根据实际情况调整路径
    
    if not os.path.exists(comments_folder):
        print(f"错误：找不到文件夹 {comments_folder}")
        return
    
    # 处理所有评论并生成chunks
    chunks, metadata, sources = processor.process_all_comments(
        comments_folder, 
        chunk_size=500, 
        overlap=100
    )
    
    if not chunks:
        print("没有生成任何chunks，请检查文件内容")
        return
    
    # 存储到ChromaDB
    store_in_chromadb(collection, chunks, metadata)
    
    # 验证存储
    collection_count = collection.count()
    print(f"ChromaDB集合中现有 {collection_count} 个文档")
    
    # 示例查询测试
    print("\n进行示例查询测试...")
    results = collection.query(
        query_texts=["测试查询"],  # 可以替换为实际的关键词
        n_results=3
    )
    
    print("示例查询结果:")
    for i, doc in enumerate(results['documents'][0]):
        print(f"\n--- 结果 {i+1} ---")
        print(f"文档: {doc[:200]}...")  # 只显示前200个字符
        print(f"元数据: {results['metadatas'][0][i]}")

if __name__ == "__main__":
    main()