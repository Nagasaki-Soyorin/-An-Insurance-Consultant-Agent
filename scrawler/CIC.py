import requests_html
import random
import time
import json
import base64
from base64 import b64decode
from Crypto.Cipher import AES
import struct
from Crypto.Hash import SHA256
# from gmssl import sm2, sm3, sm4, func
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # 用于元素定位
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
from datetime import datetime, timedelta
import time
import hashlib 
import requests
from functools import wraps
import json
import calendar
import threading 
from openpyxl import load_workbook
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor ,ProcessPoolExecutor,as_completed
import concurrent.futures
import pprint
import time
from functools import wraps
# 
# 导入必要参数
try:
    # 优先用于被 main.py 调用时（包内相对导入）
    from .web_params import cookies, headers, cookies_detail,headers_detail,params,json_data
    
except ImportError:
    from web_params import cookies, headers, cookies_detail,headers_detail,params,json_data

def decrypt_aes(e, t=None, n=None):
    # 将字符串中的 "_" 替换为 "+"
    e = e.replace("_", "+")
 
    # 如果 t 和 n 被提供，进行编码转换
    if t and n:
        a = t.encode('utf-8')
        o = n.encode('utf-8')
    else:
        # 如果未提供 t 和 n，默认处理
        # 从web调试过程中获取的 words 和 sigBytes
        a_words = [811873078, 1664497716, 909534512, 912406841]
        o_words = [808989744, 1697789748, 942748209, 875783733]
        # 将 words 转换为字节数组
        a = b''.join(struct.pack('>I', word) for word in a_words)
        o = b''.join(struct.pack('>I', word) for word in o_words)
    # 将 Base64 编码的字符串解码
    r = b64decode(e)
    # 使用密钥和初始向量创建 AES 解密器
    cipher = AES.new(a, AES.MODE_CBC, o)
    # 解密数据
    decrypted_data = cipher.decrypt(r)
    # 移除 ZeroPadding 填充字节
    decrypted_data = decrypted_data.rstrip(b'\x00')
    # 转换为字符串并返回
    return json.loads(decrypted_data.decode('utf-8'))
 
# # 示例调用，假设 t 和 n 是密钥和 IV 的字符串形式
# e = "blcWLsbHYQ5vv79e30zdQ7cyPC8nLbJ_00hFjKs6FQX16WTWPP4h45Wt4UMqZzTsL0HtHuQT2UVys4UddrDY7M8KrkKNALS2U6xYSW2AZYZjMBBC_VHAdLL2NPSlAj05acoyHKwNcWdIO713Jdb_t70oiLlJw3StwMsJvBdph3beCJSPKy88VuKsyda_itOQD3sqOV5uXpSgOLDc5qh1_URQ8gNHQ22KVHD8i0tawYFk1Zd/thQc9XknHiqmsky3Bk5ahQCgfP2A72s/LNm2H2PmTdfiRw02yZcEx8m5wDRtX9jPXh4dcmjClTsspCEGsXf/oss22JL5Ah3ty4QzInjkP7Wan_ulsZC8JbYzhbUjTUz0PFrTj2MPJmeFoRJDt6x_YqR32AaiMGBQfhkGokp2MJjPTGEPdAhk_9OJH9gI34L7iQO5LQwznxWPLujwtD1avYRyV_mFev4OHhAvaf66g0NwWpnyuYiqRTHE3dxEfFVjZNkhAoo0SDKGR93y3UpxvWdK5JYwzwfMMHOVAQbuhIRIcNs3UAdJvQ5bWnmHfRzmXSgY4v4iArTwWCAGOEqxZqTHOsw4FPqVehvmUg36t8kxZ0iwkqg5OPVkb3YHIC3TggIWWyOfIaFoqJ_0jjCId_UM0wGVcgs0cG6fCD8vBXwtpfMojTNNL3G7yMaiPinllS1Eq6J1Tj1gmw/zKJHF9KAHjygVWuwdFFuCImfHT_Sji_qvys1TudTOgrq_uZ0NG5mOoFYOpkgE2CRZYcGlkVySPmssE2gIaWJitnBYhNbf7CWVgy9nWQhChhp6/C2Up5VT4am3jl5LMy5pwHOKRe3alW96TgVHZCMcixKjhioh7svrK6nLi7vFvBH5QM2Wx9OTD5wkUKu09mjFrmIcvDQkHkLpzcvjZFQSPjAymLjwCtqmfGw/LnEhUCqLti0zN71/tDydU3DCIshAEUXcq3VKUyYzbcxTh6IPrKCPtiGBxfotwVE_ej/tmUzeBwXx31vWebEdI2KX2DZFyrVqzp35y5BYvsZ1lXJ9qAwJHE_o9Q4PaQn49kUufQF/wM/cl7Rg53nmXtc9wFJZVEYUnG8zdRIEsYkpOFMPIyvA53VA/F7YiyLd9q2OM7vSajx1C63kmHWaANsmdBoIjiudim9NfJ7LqniLkPRDP0PtOV8geh1YdzfKBm3b0zYfuaZhyhsyal6eJvLa3j8il5IB/qR9ESi/lyUAXH_2BUADLHSWcZycpwTydu4wwDPplsdPUAFyuuWbBfJ_4xPVWivJkF38cylW99LAHorSN3jhsUKCdSGIzETq/nIH2J/n0Reyo3YhMgppgtaxFEOM1N3s_iCKWCpXw8b2zDfnnJAek3hiehMrtDckFat9RUfHz9EOSOaYdcjLh6HDRchz1pWgYgFTIXHmcsRd6gxA6ffOtYIt698/nBf6K0/POGB6FwqsgQ10NxaLFKWNTcjL6vcVg9fpHV1WXeXzDlYkBKhzpyq1wJ4ffAfuytjizMf6zdFSqsGKJcsThwZsa6FZfBGADFkZseA2tAoAn3jw_ujUAWWaJvtz9iEfGnx1ma3HOt/YGTAanHLuO3GQ1SXutjiuBQUGO7r4fXx5fu74bjKCDOiovId5XFFrFlE2fGYyKrJPy3pSkGlggJL3xQNbIqdkVFZf2_/NF1wtTTA_YBZefVWWPvu5B3uX5ATKqbRn6GVUCPBKP4RiQwQNmLOH0DdjPETnv4bervc_/eNur_IBEmk2Cg2GsxwDk9rDK3jDitkreM0wbb9UnwnokV__kfgCMDNNSuUXHhzgRME6aXfq9ONQTbY8o7dyfd_vqMPzpUy/t_ta28eo_dRjNCk12bp4CApcWZgXRK63iPH7GLFgP8l1l_Zqps/y_O8_MJZTSBPLFEOtwP5VTes8WK36gcWXqT0llfoAEq1PPadpLuLSvRq4Lb2_32bUESGozr0lJRuW1ayk0O82RwPrLWripILqU/ZPMUnYhiSkss0LEe3F8yvn3DRlhnBcvcoUh/dBs4f3el4xIWM_hcejXCU6ZHXF0l8M5D0680yqGDteCdIDpgdTs4z5fG61X4QNJqRy36QhsPkA2rvohTz/PSzud5J0IUyLNdZGEDeMi7CNR8BWyqnzj3UdTZgTnJUposOeIWWEwTKso/mVHYZ6SQxnhD3Hg2thzAYu7ZyN8MnzpiNWBnFhyMxX/hTUcBD6iQbUdazg0q_I9gaHSX7bRmueTp4hqrgo_0FXuX5HvGJIzceHW8Y8SQoICG8Otk4TvYaHRHinWKwcpFphgoi9WodyrLIm8b/SA3/7H06mQmGVwuggXzeZXXdLNjI3F5TUr9AZUnXUgYCs_n7faID5ZYQH4ErvwSvtEeGs_GTLweoigu38jZ4qXPEwpAgJkJA1CUpOkQWR2JxwDmQByQw1KaDpGUX5h3gHYEmMLQf_WQb58uxxHjpNr5Fyg6lC60KbNkkB9l9ERkmdcI/Ysfw/RqxvHAkD6BQ2gntdi6OjdltlAz2cJJEfy8/idTRCNLlUWzLksPgHjFqZds2orzOCZ3tpDORvAEgnWPHzelw8SFOGwIQhHC3NUO255kmsUJzESiN03P9TZB87aLvAMhB5Vy43vlgUiSsdBFEoWcblCeWbyfR24nuN3ks/8tH9Ajw1JSJv7hWlC2Zu2ulz69bZoYLUTc3fQMwiNzX0TcckoQ_e0fwbfU2TNeY0wjeG6qGqPCMTdJPY2nSIzy/HxBpWchZciT1Lv6rVcL0gzzhATnPltF4ljOfHqC8Z4AdNvyhZ/MVySV_mOecD7DvDyaXIifqIfLJZPd8EQc0evDTgwqa7o/Y45gV/Ws0tWLH3KUtGmni7Pob9eLwi4y9qxTP8B8NICM91qfFwH4CsJzGRC0JcOgzfGuJXT94wFEKTQfPrEe29FRw7qV84r6weIIYSYPQVMRaR7jefyTnhIANtxY3tswRV/BIpT1PNaTbYfbkUbXc4YAdUlaQymU86lCnDdtjvzps2bZHZm04EsviIeW263d1wESDrrIV9JDJtqHmS2mseZgQXf49DRicj9/GRLNhSLXU7atTBktXV/2QV_/QARlu3JDnHicw9wcRC09iXOZ9m5kqJIsk/NmkWW2rnvTkprqAgyFTxAMs17rVWdhljuVhdeOL90IWvKLFo4vo4X19B/s9RurABaGSff1sNnUnSbi57H_eu5hzFZQv59Vki1nXXehfxeqceJl9Q3OdOltgO3Dxfajm23o3RPHTgSkEjzD8lsqn8rvIks4DE79dRJ4G2hn1E9jH11CUMFJP_3peWpbJja3YtQ7MNN1EV5/vmW4fpKdb0AOzl7DD7j45ClyYjBS4LyHjHZuJsQmJABT/9kayW4VLhN3dKWh9N0Km6uPErLuCxWXYmbrOZhM4qaKfgOpRXrONLloLxinFLYim/aYFdFZ7_SPNfIoEhvZu6GZaZBZnAEecrqV1kFg4IRRZ/ccUKUmsRNBwdzjpPORqxWQNq15qC8u2968kwvSpIXI2zCChZxfM5_YZKZW8xq_ZjPUS_RTnGyGEwnxAIT2AYTfwmKi4h07eS7HZ9Qh8Bg7rb_B47Nar_qs8W9QKWzIv_xjQkpzpw2khlXr1504pXFNvtJ/DdNsWMEAV/45hrvEeM2BTJWaDSx/5DlFV0EOmhKee6oew3/dqMp691FBce1Z_lvx1LF7cXTsUD9yBYXw2xgVCuK2M7Ls32_VTh3WIwTp3xLHohDAucr7QQ36rlRu9E92uNSZVLoa/Mtx2i9mEYfXhWPfJg0dsuwM7Uw535FljQTge_adYyzttRMpXVwmjxpFn4PuhXdO8Y6ft2KiF09s5kPHTKfu7ArykK95FrGRYd_ppoP_tkq2IueS84aPhFdCz4XU6Uc0P7koT0UWSIRPBT6n1ZbP58desBkGS4nC9H7qJ3uc4rUF/9bWMKRLlsnuP/Qn/988FORJcXjAaMOuvPneLXCuLgq_Wt3lnKkcUB7VF/YT6mSLKBYBZ3VkYEIFs4GbziU8P7od7fXmlW6s6EAa45biDUvZ1yx/VlZGLa0WKWwNabwtXRlcuSWnDmdImMzTiorMpA7/GuFcwR80QPNgD32rZstzUTkmzjOgHUebAFFvrj3xuT6Or8UgN5q8nJGkx1uaImsR7ISNwYDHcMuyhBjeMaMUCThmmmlWq/BTWCSB8Xq2dgDDaXv1vCQXLmhhm9cf4d8dNuKcTNTiYDCAUIq2Txt0jCmHSiHAgmcRTOnSETMBJghw0Lb0Y7pnmvTJXtImr8i0tOS2AM/vTzy_DCySemmVllZsNIzEdcw8qNElLxyK7Opa2H3/HsnsjlNamOug2keC4/SSESbj1fQ3FJ3WajlQ428aZNxmbQMntvyq_a_kJtO4cS5MpXrQC/Ec9LKNW_6KUusqyCiDXs2JDlGSteYUBVh9kLkaJ5PthvwRAprmmOfAZ98LD_F7sJoxmHBtLs2Gn38mhfs3Ow1zQQ71H87Y6_mLXh4MUO3IBFH3bw1d8owKZm9NmrJxkRarGJfLhm1zcRxoQFGhl27ElcY3i_tkx0ohuv4vcl9a7zPlD3BFVUMl62CGqQQTQG9FHv/RxMRG71JkuhEJ2LoBbT0p2Js/ICN85/9ttYn/39wrZs/M9HSGRLKcHbsG65ScUR66sbcEjP/2dFWifvwko9Cx/S8GwYCqwSZKtljHjt_g6PSxa_8z7unG/XejmzA5v7KSOmZgaEMAWSAUdATzp9mzY8/Gz5lZ8BzATe6F2uk2HWLTJ7Ri8rtz9E/1lEW_db98D8356xUBbbS9HTZFrU5KxRcqLrkVC0aHXArlCpmhgD6qZ4YhEoF4sjy4YnY_hH4Uz_Jnc0hqyxha42wBJ0ZBzx0SFhPfhCFeyMEnlq2wXyHVX4EHj1fsGvsdxVOSjca8yL6mT3TDs2Du1iRQLGatfobYWQhg69DHQp9wz8xl9LzMycgbM="
# t = None
# n = None
# result = decrypt_aes(e)
# print(result)




def retry(max_attempts=5, delay=10, exceptions=(Exception,)):
    """
    重试装饰器
    
    参数:
        max_attempts: 最大尝试次数 (默认3次)
        delay: 每次重试之间的延迟(秒)
        exceptions: 触发重试的异常类型(默认为所有异常)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        print(f"尝试 {attempt} 失败，{delay}秒后重试... 错误: {str(e)}")
                        time.sleep(delay)
            raise Exception(f"函数 {func.__name__} 执行失败，已尝试 {max_attempts} 次") from last_exception
        return wrapper
    return decorator

class data_crawler(object):
    
    def __init__(self,cookies: dict,headers: dict, json_data = None, params = None,proxies = None,):
        print("爬取示例正在初始化")
        self.cookies = cookies
        self.headers = headers
        self.json_data = json_data
        self.params = params
        self.proxies = proxies
        
    @retry(max_attempts=5, delay=20)
    def get_data(self)-> dict:

        print("爬取函数成功初始化")
        response = requests.post(
            'https://tiaokuan.iachina.cn/sinopipi/prodtermsinfo/selectConsumerList',
            cookies=self.cookies,
            headers=self.headers,
            json=self.json_data,
            params = self.params,
            proxies=self.proxies
        )
#         print(response.text)
        data = json.loads(response.text)["data"]
        
        return  decrypt_aes(data)['records']

class data_crawler_detail(object):
    
    def __init__(self,cookies: dict,headers: dict,json_data = None, params = None,proxies = None):
        self.cookies = cookies
        self.headers = headers
        self.json_data = json_data
        self.params = params
        self.proxies = proxies
        
    @retry(max_attempts=5, delay=20)
    def get_data(self)-> dict:
        url = 'https://tiaokuan.iachina.cn/sinopipi/salemaintaapply/getHtmlData'
#         print(url)
        response = requests.get(
            url,
            cookies=self.cookies,
            headers=self.headers,
            json=self.json_data,
            params = self.params,
            proxies=self.proxies
        )
#         print(response.text)
        data = json.loads(response.text)["data"]
        
        return  decrypt_aes(data)

def collect_data(prod_list):   
    
    """在总体爬取获得所有产品的id后，用于根据id爬取所有的详细信息"""
    
    data_dict, counter  = {}, 0
    for item in prod_list:
        # 调整详细页面的请求参数
        params["termsno"] = item['termsno']
        
        # 生成爬取实例并爬取
        Crawler_detail = data_crawler_detail(cookies_detail,headers_detail,params = params)
#         max_try , trytimes= 5 ,0
        data = Crawler_detail.get_data()

        # 获得返回值 将数据储存在data_dict中 key为产品名 values为产品详细信息 是一个列表
        """注意有些产品会重复上市，所以这里需要用不重复的termno作为唯一标识符"""
        data_dict[item['termsno']] = data["prodVo"]["base"]
        
        #为data["prodVo"]["base"]补充销售时间数据 
        try:
            saledate = {'name': '开始销售时间：', 'value': item['saledate']}
            data["prodVo"]["base"].append(saledate)
        except Exception as e:
            print("时间未知")
        #暂停一会 避免给封IP
        random_num = random.uniform(0.5, 1.5)
        time.sleep(random_num)
        counter += 1
        print(counter)
    return data_dict
    
def collect_data_single(prod_list,prodname:str):   
    
    """在总体爬取获得所有产品的id后，用于根据id爬取所有的详细信息"""
    
    
    data_dict, counter  = {}, 0
    for item in prod_list:
        # 调整详细页面的请求参数
        params["termsno"] = item['termsno']
        
        # 生成爬取实例并爬取
        Crawler_detail = data_crawler_detail(cookies_detail,headers_detail,params = params)
#         max_try , trytimes= 5 ,0
        data = Crawler_detail.get_data()

        # 获得返回值 将数据储存在data_dict中 key为产品名 values为产品详细信息 是一个列表
        """注意有些产品会重复上市，所以这里需要用不重复的termno作为唯一标识符"""
        data_dict[item['termsno']] = data["prodVo"]["base"]
        
        #为data["prodVo"]["base"]补充销售时间数据 
        try:
            saledate = {'name': '开始销售时间：', 'value': item['saledate']}
            data["prodVo"]["base"].append(saledate)
        except Exception as e:
            print("时间未知")
        #暂停一会 避免给封IP
        random_num = random.uniform(0.5, 1.5)
        time.sleep(random_num)
        counter += 1
        print(counter)
        print(data["prodVo"]["base"][1]["value"] )
        # 判断是否已经命中缓存
        if data["prodVo"]["base"][1]["value"] == prodname:
            

            break

    return data_dict
       
    
    
def main():
    
    """这是一个跳过验证码环节的简便产品备案信息获取小工具"""
    
    #第一步循环查找需要的保险产品
    while True:
        name = input("请输入您需要查找的健康险产品名称，允许模糊搜索:   ")
        json_data['prodname'] = name 
        json_data["pageNum"] = 1
        json_data["pageSize"] = 10
        Crawler_aggregate = data_crawler(cookies,headers,json_data)
        prod_list = Crawler_aggregate.get_data()
        name_list = [item['prodname'] for item in prod_list]
        if len(name_list) == 1:
            break
        elif len(name_list) == 0:
            print("查无此险，请检查输入,或关闭本页面")
#             break
#         print()
        print('根据您的输入，找到了以下产品')
        for name_ in name_list:
            print(name_)
        print()
        print("请复制您需要详细查找的产品名称")
#         print()
    
    
    params["termsno"] = prod_list[0]['termsno']
    Crawler_detail = data_crawler_detail(cookies_detail,headers_detail,params = params)
    data = Crawler_detail.get_data()
    detail = data["prodVo"]["base"]
    saledate = {'name': '开始销售时间：', 'value': item['saledate']}
    detail.append(saledate)
    print(pd.DataFrame(detail).set_index('name').T)







# def get_raw_insurance_for_AI(json_detail:dict):
    
#     """根据AI传入的json 检查最近的产品
#     传入应当是一个dict"""
    
#     # 获取所有保险产品的列表
#     json_data["pageNum"] = 0
#     json_data["pageSize"] = 100
#     json_data["prodtypecode"] = 'PubNewProdTypeCode_02'
#     Crawler_aggregate = data_crawler(cookies,headers,json_data)
#     prod_list = Crawler_aggregate.get_data()
    
#     # 开始爬取保险产品
#     while True:
       
       
       
#        break 
        

    # data_dict = collect_data(prod_list)

if __name__ == "__main__":
    for page in range(0,1):
        
        """爬取首页 获得产品的id信息"""
        json_data["pageNum"] = page
        json_data["pageSize"] = 10
        json_data["prodtypecode"] = 'PubNewProdTypeCode_02'
        Crawler_aggregate = data_crawler(cookies,headers,json_data)
        prod_list = Crawler_aggregate.get_data()


        [print(prod) for prod in prod_list]
        """根据id信息修改请求参数，获取每个产品的详细信息"""
        data_dict = collect_data(prod_list)
        print(data_dict)
        input()
        final_data = pd.DataFrame()
        for item in data_dict.values():
            prod_detail = pd.DataFrame(item).set_index('name').T
            final_data = pd.concat( [prod_detail, final_data], join="outer")
        from IO_data import save_insurance_data
        save_insurance_data(final_data)
        # final_data.to_excel(f"./Insurance_Data/Health Inusrance/寿险爬取数据集合{json_data['pageNum']}.xlsx")
#         final_data