import scrapy
import os
import sqlite3
from urllib.parse import urlencode
from urllib.parse import urlparse
import json
from datetime import datetime
import random
import time


def create_google_url(query, site=''):  # 构建针对Google搜索的url
    google_dict = {'q': query, 'num': 10 }  # 创建字典，包括查询和结果数量
    if site:  # 如果提供了特定网站
        web = urlparse(site).netloc  # 提取网站的域名部分
        google_dict['as_sitesearch'] = web  # 将域名添加到查询字典中
        return 'https://www.google.com/search?' + urlencode(google_dict)
    return 'https://www.google.com/search?' + urlencode(google_dict)  ## 返回构建好的 URL

class GoogleSpiderSpider(scrapy.Spider):
    name = "googlespider1"
    allowed_domains = ['google.com']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'RETRY_TIMES': 3,
        'DOWNLOAD_DELAY': 1  # 限制请求之间的延迟时间，防止过于频繁的请求
        , 'RETRY_HTTP_CODES': [502, 503, 504, 408]
    }

    # 创建数据库连接并初始化表
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 连接 SQLite 数据库
        self.conn = sqlite3.connect('web_data.db')
        self.cursor = self.conn.cursor()
        # 创建数据表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS g_test_webpages (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        title TEXT,
                                        html_file_path TEXT,
                                        link TEXT,
                                        position INTEGER,
                                        date TEXT
                                      )''')



    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',  # 增加 Accept-Language 头，模拟更真实的浏览器行为
            'Accept-Encoding': 'gzip, deflate, br'
        }

        # 中文基础关键词
        ch_base_queries = ['人工智能']

        # 中文拓展关键词
        ch_extension_queries = [
            '应用'
        ]
        # 中文组合生成查询
        ch_combined_queries = []

        for base in ch_base_queries:
            for extension in ch_extension_queries:
                query = f"{base} AND {extension}"
                ch_combined_queries.append(query)

        # 发送请求到每个查询
        for query in ch_combined_queries:
            self.logger.debug(f"Processing query: {query}")  # 打印当前正在处理的查询
            url = create_google_url(query)  # 创建 Google 搜索的 URL
            yield scrapy.Request(url, callback=self.parse, headers=headers)

            '''# 随机等待 1 到 3 秒之间的时间
            time.sleep(random.uniform(3, 5))
'''

        def parse_search_results(self, response):
            self.logger.debug(f"Parsing search result page {response.url}")

            # 解析搜索结果页面
            search_results = response.css('div.g')  # Google 搜索结果的父元素是 <div class="g">

            # 遍历每个搜索结果并提取链接
            for result in search_results:
                title = result.css('h3::text').get()  # 提取搜索结果的标题
                link = result.css('a::attr(href)').get()  # 提取搜索结果的链接

                if link:
                    # 处理相对链接
                    if link.startswith('/url?q='):
                        link = link[7:]  # 移除 "/url?q=" 部分

                    # 确保链接是一个有效的完整 URL
                    if link.startswith('http'):
                        # 请求并爬取该页面的 HTML
                        yield scrapy.Request(link, callback=self.parse_article, meta={'title': title, 'link': link})

                    # 随机等待时间，避免过于频繁的请求
                    time.sleep(random.uniform(1, 3))


    '''def parse(self, response):
        self.logger.debug(f"Response status code: {response.status}")

        if response.status != 200:
            self.logger.error(f"Request failed with status code: {response.status} for URL: {response.url}")
            return  # 如果请求失败，跳过

        # 打印返回的 HTML 内容，查看是否包含验证码或者其他异常页面
        self.logger.debug(f"Response content: {response.text[:1000]}")  # 打印前 1000 个字符

        # 直接获取并保存 HTML 内容
        html_content = response.text
        title = response.xpath('//title/text()').get()  # 从网页中提取标题
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 创建目录存放 HTML 文件
        os.makedirs('html_files', exist_ok=True)
        file_name = f'html_files/{title}_{dt}.html'.replace(" ", "_").replace(":", "_").replace("/", "_")

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f"Saved HTML file at: {file_name}")

        # 你可以选择将 HTML 内容保存到数据库或者进行其他处理
'''

    def parse_article(self, response):
        # 获取页面内容并保存 HTML
        title = response.meta['title']
        link = response.meta['link']
        html_content = response.text
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 创建目录并保存 HTML 文件
        os.makedirs('html_files', exist_ok=True)
        file_name = f'html_files/{title}_{dt}.html'.replace(" ", "_").replace(":", "_").replace("/", "_")

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.logger.info(f"Saved HTML file at: {file_name}")