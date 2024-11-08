import scrapy
import os
import sqlite3
from urllib.parse import urlencode
from urllib.parse import urlparse
import json
from datetime import datetime
import random
import time

API_KEY = '5466737fb5d05dc60687826732eb17db'  # 使用scraperAPI代理地址池


def get_url(url, country_code='us'):
    payload = {'api_key': API_KEY, 'url': url, 'autoparse': 'true', 'country_code': country_code}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    # 打印代理请求的 URL
    print(f"Requesting URL: {proxy_url}")
    return proxy_url


def create_bing_url(query, site=''):  # 构建针对Google搜索的url
    google_dict = {'q': query, 'num': 100, }  # 创建字典，包括查询和结果数量
    if site:  # 如果提供了特定网站
        web = urlparse(site).netloc  # 提取网站的域名部分
        google_dict['as_sitesearch'] = web  # 将域名添加到查询字典中
        return 'https://www.bing.com/search?' + urlencode(google_dict)
    return 'https://www.bing.com/search?' + urlencode(google_dict)  ## 返回构建好的 URL


class GoogleSpiderSpider(scrapy.Spider):
    name = "bing_spider"
    allowed_domains = ['api.scraperapi.com']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'RETRY_TIMES': 3,
        'DOWNLOAD_DELAY': 1  # 限制请求之间的延迟时间，
        , 'RETRY_HTTP_CODES': [502, 503, 504, 408]
    }
    start_urls = [
        'https://www.bing.com/search?q=AI'  # 这里可以修改为其他搜索关键词
    ]

    # 创建数据库连接并初始化表
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 连接 SQLite 数据库
        self.conn = sqlite3.connect('web_data.db')
        self.cursor = self.conn.cursor()
        # 创建数据表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bing_test_webpages (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    title TEXT,
                                    html_file_path TEXT,
                                    link TEXT,
                                    position INTEGER,
                                    date TEXT
                                  )''')

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 中文基础关键词
        ch_base_queries = ['人工智能', 'AI']

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

        # 确保查询生成了正确的组合
        self.logger.debug(f"Generated combined queries: {ch_combined_queries}")

        '''


            '使用场景',
            '取代行业',
            '发展历程',            
            '技术的影响',
            '挑战和机遇',
            '未来趋势',
            '伦理问题',
            '取代人类',
            '短板',
            '不能做到的事情'

        # 英文基础关键词
        en_base_queries = ['Artificial Intelligence', 'AI']

        # 英文拓展关键词
        en_extension_queries = [
            'applications',
            'development history',
            'impact of AI technology',
            'challenges and opportunities',
            'future trends',
            'ethical issues'
        ]
        # 英文组合生成查询
        en_combined_queries = []

        for base in en_base_queries:
            for extension in en_extension_queries:
                query = f"{base} AND {extension}"
                en_combined_queries.append(query)
        '''
        '''
                # 输出组合查询
                for query in en_combined_queries:
                    print(query)
                '''
        # 将查询分成多个批次
        batch_size = 2  # 每批处理 5 个查询
        for i in range(0, len(ch_combined_queries), batch_size):
            batch_queries = ch_combined_queries[i:i + batch_size]
            for query in batch_queries:
                self.logger.debug(f"Processing query: {query}")  # 打印当前正在处理的查询
                url = create_bing_url(query)
                yield scrapy.Request(get_url(url), callback=self.parse, meta={'pos': 0})

                # 随机化请求间隔（例如 1 到 3 秒之间的随机延迟）
                time.sleep(random.uniform(1, 3))  # 等待 1 到 3 秒之间的随机时间

        '''#发送请求
        for query in ch_combined_queries:
            url = create_google_url(query)
            yield scrapy.Request(get_url(url), callback=self.parse, meta={'pos': 0})'''
        '''
         for query in en_combined_queries:
            url = create_google_url(query)
            yield scrapy.Request(get_url(url), callback=self.parse, meta={'pos': 0})

        '''

    def parse_article(self, response):
        title = response.meta['title']
        pos = response.meta['position']
        dt = response.meta['date']
        link = response.url

        # 创建目录存放 HTML 文件
        os.makedirs('bing_files', exist_ok=True)
        file_name = f'bing_files/{title}_{pos}.html'.replace(" ", "_")  # 去掉空格以便命名

        if os.path.exists(file_name):
            self.logger.info(f"bing-HTML file saved at: {file_name}")
        else:
            self.logger.error(f"Failed to save bing-HTML file at: {file_name}")

        # 将 HTML 源代码保存为文件
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(response.text)

        # 从网页中提取正文内容（假设使用 CSS 选择器）
        # body_text = ''.join(response.css('div.content::text').getall())

        # 将数据存储到数据库中
        try:
            self.cursor.execute('''INSERT INTO bing_test_webpages (title, html_file_path, link, position, date)
                                      VALUES (?, ?, ?, ?, ?)''', (title, file_name, link, pos, dt))
            self.conn.commit()  # 提交更改

            # 输出日志，确认数据已插入
            self.logger.info(f"Inserted data into database: title={title}, link={link}, position={pos}, date={dt}")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting data into database: {e}")

    def parse(self, response):
        self.logger.debug(f"Response status code: {response.status}")

        if response.status != 200:
            self.logger.error(f"Request failed with status code: {response.status} for URL: {response.url}")
            return  # 如果请求失败，跳过

        try:
            di = json.loads(response.text)
            self.logger.debug(f"Received JSON: {json.dumps(di, indent=2)}")  # 打印 JSON 内容
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON response")
            return
        pos = response.meta['pos']
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        MAX_PAGES = 3  # 限制每个查询抓取的最大页数
        # 限制页面数
        page_number = response.meta.get('page_number', 1)
        if page_number > MAX_PAGES:
            return  # 超过最大页面数，停止爬取

        if 'organic_results' in di:
            for result in di['organic_results']:
                title = result['title']
                link = result['link']

            # 发送请求到网页链接，以提取正文
            yield scrapy.Request(link, callback=self.parse_article, meta={'title': title, 'position': pos, 'date': dt})
            pos += 1
        else:
            self.logger.warning("No organic results found in the response.")

        # 处理下一页
        next_page = di.get('pagination', {}).get('nextPageUrl')
        if next_page:
            yield scrapy.Request(get_url(next_page), callback=self.parse, meta={'pos': pos})

    def close(self, reason):
        # 关闭数据库连接
        self.conn.close()





