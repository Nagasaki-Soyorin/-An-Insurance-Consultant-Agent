import pandas as pd
import os
from pathlib import Path
import numpy as np
from datetime import datetime
try:
    # 优先用于被 main.py 调用时（包内相对导入）
    from .CIC import collect_data_single, data_crawler
    from .web_params import cookies, headers, cookies_detail,headers_detail,params,json_data
except ImportError:
    # fallback：用于你直接调试 IO_data.py 时
    from CIC import collect_data_single, data_crawler
    from web_params import cookies, headers, cookies_detail,headers_detail,params,json_data

def df_to_frontend(df):
    # 处理 nan、None
    df = df.replace({np.nan: ""})

    # 处理带换行符的字符串
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return {
        "response": "以下是当前保险产品市场概览数据：",
        "response_type": "dataframe",
        "dataframe": {
            "columns": df.columns.astype(str).str.replace('\n', '').tolist(),
            "data": df.astype(str).values.tolist()
        }
    }

def get_today_date():
    """返回今天的日期"""
    return datetime.now().strftime("%Y-%m-%d")

def is_cache_from_today(base_path="./Insurance_Data/Health Insurance/"):
    """
    判断缓存是否是今天之内保存的
    
    Returns:
        bool: 如果缓存是今天保存的返回True，否则返回False
    """
    base_dir = Path(base_path)
    if not base_dir.exists():
        return False
    
    # 查找所有包含日期的xlsx文件
    cache_files = []
    for file in base_dir.glob("*.xlsx"):
        if "insurance_data" in file.stem:
            cache_files.append(file)
    
    if not cache_files:
        return False
    
    # 按修改时间排序，取最新的文件
    latest_file = max(cache_files, key=lambda x: x.stat().st_mtime)
    
    # 从文件名中提取日期
    try:
        # 假设文件名格式为 insurance_data_YYYY-MM-DD.xlsx
        date_str = latest_file.stem.split('_')[-1]
        file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        return file_date == today
    except:
        # 如果解析失败，使用文件修改时间判断是否是今天
        file_mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
        return file_mtime.date() == datetime.now().date()

def find_latest_cache_file(base_path="./Insurance_Data/Health Insurance/"):
    """
    查找最新的缓存文件
    
    Returns:
        tuple: (文件路径, 文件日期) 如果找到则返回，否则返回 (None, None)
    """
    base_dir = Path(base_path)
    if not base_dir.exists():
        return None, None
    
    cache_files = []
    for file in base_dir.glob("*.xlsx"):
        if "insurance_data" in file.stem:
            cache_files.append(file)
    
    if not cache_files:
        return None, None
    
    # 按修改时间排序，取最新的文件
    latest_file = max(cache_files, key=lambda x: x.stat().st_mtime)
    
    # 从文件名中提取日期
    try:
        date_str = latest_file.stem.split('_')[-1]
        file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return latest_file, file_date
    except:
        file_mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
        return latest_file, file_mtime.date()

def get_last_product_name(df):
    """
    获取数据框中最后一条数据的【产品名称：】列的值
    
    Args:
        df (pd.DataFrame): 数据框
    
    Returns:
        str: 最后一条数据的【产品名称：】值，如果没有则返回None
    """
    if df is None or df.empty:
        return None
    
    # 查找包含"产品名称"的列
    product_columns = [col for col in df.columns if '产品名称' in col]
    if not product_columns:
        return None
    
    product_col = product_columns[0]
    return df[product_col].iloc[-1] if not df[product_col].isna().iloc[-1] else None

def get_insurance_data_with_cache(prod_type, crawler_function = None, base_path="./Insurance_Data/Health Insurance/"):
    """
    获取保险数据的智能缓存逻辑
    
    Args:
        crawler_function: 爬虫函数，能够逐条爬取数据
        base_path (str): 缓存文件路径
    
    Returns:
        pd.DataFrame: 保险数据
    """
    # 设置默认参数
    # print("这里？")
    prod_key = {
        "健康险":"PubNewProdTypeCode_02",
        "人寿保险":"PubNewProdTypeCode_00",
        "年金保险":"PubNewProdTypeCode_01"

    } 


    # 调整json_data
    json_data["cplbone"] = prod_key[prod_type]
    json_data["prodtypecode"] = prod_key[prod_type]

    


    # 检查是否有今天内的缓存
    if is_cache_from_today(base_path):
        cache_file, _ = find_latest_cache_file(base_path)
        if cache_file:
            print(f"使用今天内的缓存文件: {cache_file.name}")
            df = pd.read_excel(cache_file)
            # print(df)
            print({
                "columns": df.columns.tolist(),
                "data": df.values.tolist()
            })
            return pd.read_excel(cache_file, index_col=None)
    
    print("缓存过期或不存在，启动爬虫...")
    
    # 读取现有的最新缓存文件（如果有的话）
    cache_file, file_date = find_latest_cache_file(base_path)
    old_data = None
    last_product_name = None
    
    if cache_file:
        old_data = pd.read_excel(cache_file)
        last_product_name = get_last_product_name(old_data)
        print(f"找到旧缓存({file_date})，最后一条数据的产品名称: {last_product_name}")
    print("以旧缓存为界重新定位爬虫终点")
    # 启动爬虫并收集新数据
    print(cookies)
    try:
        Crawler_aggregate = data_crawler(cookies,headers,json_data)
        # print(cookies,headers,json_data)
    except Exception as e:
        print(e)
    print("成功创建爬取函数")
    prod_list = Crawler_aggregate.get_data()
    print("获取到待定产品名单")
    new_data_rows = collect_data_single(prod_list, last_product_name)
    
    if not new_data_rows:
        print("没有爬取到新数据")
        return old_data if old_data is not None else pd.DataFrame()
    
    print("成功获取产品详细数据")
    # 转换为DataFrame
    final_data = pd.DataFrame()
    for item in list(new_data_rows.values())[:-1]:
        prod_detail = pd.DataFrame(item).set_index('name').T
        final_data = pd.concat( [prod_detail, final_data], join="outer")
    # final_data = pd.DataFrame(new_data_rows)
    
    final_data = pd.concat([old_data, final_data], axis = 0)
    # 保存新数据（带今天日期）
    # save_path = Path(base_path) / f"insurance_data_{get_today_date()}.xlsx"
    save_insurance_data(final_data)
    # if old_data is not None and file_date != datetime.now().date():
    #     # 合并旧数据和新数据
    #     combined_df = pd.concat([old_data, new_df], axis=0, ignore_index=True)
    #     combined_df.to_excel(save_path, index=False)
    #     print(f"合并数据已保存: {save_path.name} (共 {len(combined_df)} 条数据)")
    #     return combined_df
    # else:
    #     # 只有新数据或今天已经有缓存但需要更新
    #     new_df.to_excel(save_path, index=False)
    #     print(f"新数据已保存: {save_path.name} (共 {len(new_df)} 条数据)")
    #     return new_df
    return final_data

def save_insurance_data(new_df, base_path="./Insurance_Data/Health Insurance/"):
    """
    保存保险数据到Excel文件，如果文件已存在则追加新数据
    
    Args:
        new_df (pd.DataFrame): 新的数据框
        base_path (str): 数据存储路径
    """
    # 确保目录存在
    Path(base_path).mkdir(parents=True, exist_ok=True)
    
    file_path = Path(base_path) / f"insurance_data_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    
    # 如果文件不存在，直接保存新数据
    if not file_path.exists():
        new_df.to_excel(file_path, index=False)
        print(f"新文件已创建，保存了 {len(new_df)} 条数据")
        return
    
    try:
        # 读取现有数据
        existing_df = pd.read_excel(file_path)
        
        # 纵向堆叠数据
        combined_df = pd.concat([existing_df, new_df], axis=0, ignore_index=True)
        
        # 保存合并后的数据
        combined_df.to_excel(file_path, index=False)
        print(f"数据已追加，现有总数据量: {len(combined_df)} 条")
        
    except Exception as e:
        print(f"保存数据时出错: {e}")






# 使用示例
if __name__ == "__main__":
    # 使用缓存逻辑获取数据
    json_data["pageNum"] = 0
    json_data["pageSize"] = 100
    json_data["prodtypecode"] = 'PubNewProdTypeCode_02'
    data = get_insurance_data_with_cache()
    # print(f"获取到 {len(data)} 条数据")