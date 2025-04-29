from search_engines import Google
import requests
import html2text
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import random
import chardet  # 用于检测编码
import re
import os

os.environ["SSL_CERT_FILE"] = ""

# model = AzureChatOpenAI(
#     openai_api_version="2024-12-01-preview",
#     deployment_name="gpt-4o",
#     azure_endpoint="https://ai-14911520644664ai275106389756.openai.azure.com/",
#     api_key="5YzhcN3wCRnFORXYl9SPWpzb7RIPRQmew0V71y0chvR6g6j8hcFOJQQJ99BDACHYHv6XJ3w3AAAAACOGFi3L",
#     max_tokens=2048,
# )

model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="sk-8d71a948abc44172ae9471247099b92b",
    openai_api_base="https://api.deepseek.com/v1",
    max_tokens=1024,
)

model = ChatOpenAI(
    model="qwen-max-latest",
    openai_api_key="sk-629fea8a62e94a9cbf4ef47827ce53e4",
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    max_tokens=2048,
)

def is_garbled(text, threshold=0.3):
    """
    检查文本是否乱码
    - threshold: 如果非中文字符占比超过该阈值，则认为乱码
    """
    # 统计非中文、非英文、非标点符号的字符数量
    non_chinese_chars = re.findall(r'[^\u4e00-\u9fa5，。！？、；：“”‘’（）【】…—\w\s]', text)
    garbled_ratio = len(non_chinese_chars) / max(1, len(text))

    # 统计其他乱码特征（如特殊符号）
    garbled_patterns = re.findall(r'[�▌║æ�ºç¨‹é‡‘è��é�’å]', text)
    garbled_ratio_1 = len(garbled_patterns) / max(1, len(text))

    return garbled_ratio > threshold or garbled_ratio_1 > threshold

def extract_text_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        # 检测编码
        detected_encoding = chardet.detect(response.content)['encoding']
        if detected_encoding:
            response.encoding = detected_encoding

        # 检查乱码
        if is_garbled(response.text):
            return (url, None, "Garbled text")
        
        # 转换为纯文本
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        return (url, converter.handle(response.text), "Success")

    except Exception as e:
        return (url, None, f"Error: {str(e)}")
    
def summarize_text(query, url, text, model):
    """单线程调用大模型进行总结"""
    messages = [
        SystemMessage("你是一个准确的信息总结者，擅长根据用户的需要，在用户给出的长文本里总结相关信息。避免含糊的描述，应该基于页面信息提供细节信息。"),
        HumanMessage(f"我想知道{query}，以下是相关文本：{text}")
    ]
    return url, model.invoke(messages)  # 返回 (URL, 总结结果)

def process_urls_with_llm(query, good_urls, model, max_workers=3):
    """
    多线程处理URL文本总结
    :param query: 用户查询（如"青岛旅游注意事项"）
    :param good_urls: 可用的URL列表 [(url1, text1), (url2, text2), ...]
    :param model: 已加载的大模型（如ChatOpenAI）
    :param max_workers: 线程数（根据API限流调整）
    :return: 完整汇总文本
    """
    full_text = ""
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [
            executor.submit(summarize_text, query, url, text, model)
            for url, text in good_urls
        ]
        
        # 实时获取结果
        for future in as_completed(futures):
            url, summary = future.result()
            print(summary.content)
            full_text += f"\nURL: {url}\n{summary}\n"
            print(f"✅ 已完成: {url}")  # 进度提示
    
    return full_text

def search(query):
    if query:
        engine = Google()
        results = engine.search(query, pages=3)
        links = results.links()

        # 随机选取最多10个URL
        selected_links = random.sample(links, min(8, len(links)))

        for item in selected_links:
            if '.pdf' in item:
                selected_links.remove(item)

        print("=" * 50)
        print(f"待抓取的URL（共 {len(selected_links)} 个）:")
        for url in selected_links:
            print(url)

        # 多线程抓取
        good_urls = []  # 存储可用的URL和文本
        garbled_urls = []  # 存储乱码或错误的URL

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(extract_text_from_url, url) for url in selected_links]

            for future in as_completed(futures):
                url, text, status = future.result()
                if text:  # 非乱码且无错误
                    good_urls.append((url, text))
                    print(f"\n✅ 成功抓取: {url}")
                else:  # 乱码或错误
                    garbled_urls.append((url, status))
                    print(f"\n❌ 丢弃乱码/错误页面: {url} - {status}")

        # 输出可用内容
        print("\n" + "=" * 50)
        print(f"有效页面: {len(good_urls)} 个")
        print(f"乱码/错误页面: {len(garbled_urls)} 个")

        if len(good_urls) == 0:
            return "无有效内容"
        full_text = process_urls_with_llm(query, good_urls, model, len(good_urls))
        return full_text
    else:
        return None

if __name__ == "__main__":
    search()