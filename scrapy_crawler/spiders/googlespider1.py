import scrapy
import os
import re
import json
import csv
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urljoin
from datetime import datetime
from scrapy_crawler.items import ScrapyCrawlerItem
from scrapy_splash import SplashRequest
from scrapy import Request
from bs4 import BeautifulSoup


'''
使用scrapy直接爬取Google响应请求的html页面
'''

def create_google_url(query, site=''):  # 构建针对Google搜索的url
    google_dict = {'q': query, 'num': 10 }  # 创建字典，包括查询和结果数量
    if site:  # 如果提供了特定网站
        web = urlparse(site).netloc  # 提取网站的域名部分
        google_dict['as_sitesearch'] = web  # 将域名添加到查询字典中
        return 'https://www.google.com/search?' + urlencode(google_dict)
    return 'https://www.google.com/search?' + urlencode(google_dict)  ## 返回构建好的 URL

class GoogleSpiderSpider(scrapy.Spider):
    keyword = ""
    name = "googlespider1"
    #allowed_domains = ['google.com']
    start_urls = ['http://google.com']

    # 数据文件路径
    csv_file_path = 'spiders/data.csv'

    # 初始化，检查文件是否存在，若存在则加载已有的标题以防止重复
    def __init__(self, *args, **kwargs):
        super(GoogleSpiderSpider, self).__init__(*args, **kwargs)
        self.existing_urls = set()  # 用于存储已存在的url，以避免重复
        # 增加csv文件每行字段大小限制
        csv.field_size_limit(10000000)  # 10MB

        def clean_file(file_path):
            # 读取文件并去除 NUL 字符
            with open(file_path, 'rb') as file:
                content = file.read()
            content = content.replace(b'\x00', b'')  # 删除 NUL 字符
            with open(file_path, 'wb') as file:
                file.write(content)

        # 清理 CSV 文件
        clean_file('spiders/data.csv')

        #重启爬虫时加载data.csv文件中所有已经存在的url
        if os.path.exists(self.csv_file_path):
            clean_file(self.csv_file_path)
            with open(self.csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.existing_urls.add(row['url'])


        # 去重文件中的内容
        self.remove_duplicates_from_csv()

    def write_to_csv(self, item):
        # 如果 CSV 文件不存在，则写入表头
        file_exists = os.path.exists(self.csv_file_path)
        is_empty = file_exists and os.path.getsize(self.csv_file_path) == 0
        with open(self.csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['title', 'url', 'last_modified', 'crawl_time', 'language', 'keyword', 'source', 'text']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if is_empty:  # 如果文件为空，则写入表头
                writer.writeheader()

            writer.writerow(item)  # 写入一行数据
        # 写入成功后，将 title 添加到 existing_titles 集合中
        self.existing_urls.add(item['url'])

    def remove_duplicates_from_csv(self):
        """去除 CSV 文件中的重复条目"""
        if not os.path.exists(self.csv_file_path):
            return  # 如果文件不存在，直接返回

        # 读取 CSV 文件并存储已存在的标题
        existing_urls = set()
        rows = []  # 用来存储去重后的所有数据行

        with open(self.csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row['url']  # 获取每一行的标题
                if title not in existing_urls:
                    existing_urls.add(title)  # 如果标题没有出现过，则添加到集合中
                    rows.append(row)  # 将此行数据添加到结果列表中

        # 重新写入去重后的数据
        with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['title', 'url', 'last_modified', 'crawl_time', 'language', 'keyword', 'source', 'text']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()  # 写入表头
            writer.writerows(rows)  # 写入去重后的数据行



    # 读取 cookies 的函数
    def load_cookies(self):
        with open('spiders/gcookies.json', 'r') as f:
            cookies = json.load(f)
        return cookies

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
        'CONCURRENT_REQUESTS' : 5,
        'RETRY_TIMES': 5,
        'DOWNLOAD_DELAY': 2  # 限制请求之间的延迟时间，防止过于频繁的请求
        , 'RETRY_HTTP_CODES': [502, 503, 504, 408],
        'RANDOMIZE_DOWNLOAD_DELAY' : True  # 启用请求延迟的随机化

    }


    # 基础关键词
    base_queries = ['人工智能']

    # 拓展关键词
    extension_queries = ['应用','典型技术']

    # 组合生成查询
    combined_queries = ['智能生命']

    def start_requests(self):

        # 加载 cookies
        cookies = self.load_cookies()

        #组合关键词
        for base in self.base_queries:
            for extension in self.extension_queries:
                query = f"{base} AND {extension}"
                self.combined_queries.append(query)

        self.logger.debug(f"所有组合查询: {self.combined_queries}")

        # 发送请求到每个查询
        for query in self.combined_queries:
            self.logger.debug(f"正在查询关键词: {query}")  # 打印当前正在处理的查询
            #self.keyword = query#在数据库中标记关键词字段
            url = create_google_url(query)  # 创建 Google 搜索的 URL
            #yield scrapy.Request(url, callback=self.parse)
            #Google搜索结果页为动态页面，使用splash加载动态页面（先打开docker）
            self.logger.debug(f"正在渲染搜索结果页面: {query}")
            yield SplashRequest(
                url,
                callback=self.parse,
                args={'wait': 5},  # 等待时间，确保页面加载完成
                endpoint='render.html',
                #allow_redirects=True,
                dont_filter=True,
                meta={'keyword' : query}#meta 传递关键词
                #resource_timeout = 10  # 资源加载的超时时间
            )
            #self.logger.debug(f"渲染完成: {query}")



    # 判断是否为动态网页
    def is_dynamic(self,html_source):
        # 检查是否有动态框架或脚本的标志
        dynamic_indicators = [
            "React", "Vue", "Angular", "webpack", "__NUXT__",
            "XMLHttpRequest", "fetch", "axios",
            "window.onload", "document.ready", "DOMContentLoaded",
            "window.parent.postMessage"
        ]

        # 检查关键字
        for indicator in dynamic_indicators:
            if indicator in html_source:
                return True

        # 检查 JSON 数据或数据脚本
        if re.search(r'<script[^>]*type="application/json"[^>]*>', html_source):
            return True

        if re.search(r'document\.createElement\(["\']script["\']\)', html_source):
            return True

        # 检查内容占位符
        if re.search(r'{{.*?}}', html_source):
            return True
        return False

    # 调用 is_dynamic 方法判断页面类型
    def check_dynamic(self,response):
        #通过标题判断之前是否爬取过该网页
        url = response.url
        if url and url not in self.existing_urls:
            self.existing_urls.add(url)  # 将标题添加到已爬取的集合中
        else:
            self.logger.info(f"URL: {url} 已存在，跳过此网页")
            return

        # 从 response.meta 获取 'keyword' 值
        keyword = response.meta.get('keyword')
        self.logger.info(f"网页搜索关键词: {keyword}")

        if self.is_dynamic(response.text):
            # 如果是动态网页，使用 Splash 渲染页面,再调用 parse_article
            self.logger.info(f"动态网页: {response.url}，使用 Splash 渲染")

            yield SplashRequest(response.url, self.parse_article, args={'wait': 10, 'timeout': 60},meta={'keyword':keyword})
        else:
            # 如果不是动态网页，直接调用 parse_article
            self.logger.info(f"静态网页: {response.url}，直接解析")
            yield self.parse_article(response)



    #爬取搜索结果页，获取每个搜索结果的url列表
    def parse(self, response):

        keyword = response.meta.get('keyword')  # 获取对应关键词
        self.logger.debug(f"解析搜索结果页面时获取的关键词: {keyword}")  # 打印关键词

        self.logger.debug(f"响应状态码: {response.status}")

        if response.status != 200:
            self.logger.error(f"请求失败，状态码: {response.status} ， URL: {response.url}")
            return  # 如果请求失败，跳过


        links = response.xpath('//div[contains(@class, "egMi0") and contains(@class, "kCrY")]/a/@href').extract()
        self.logger.debug(f'匹配到的搜索结果URL数: {len(links)}')  # 输出匹配到的链接数量

        # 定义过滤 YouTube 链接的正则表达式
        youtube_pattern = r'https?://(?:www\.)?youtube\.com/watch.*'
        # 去除无效链接
        valid_links = [link.split('&')[0]#去掉无关参数
                      for link in links
                      if all(x not in link for x in ['google.com/url', 'youtube.com/watch', 'youtu.be',
                                                    'google.com/preferences',  # Search settings
                                                    'google.com/advanced_search',  # Advanced search
                                                    'google.com/maps',
                                                    'google.com/terms',  # Terms of service
                                                    'google.com/policies',  # Policies page
                                                    'google.com/settings',  # Any general settings link
                                                    'accounts.google.com',# Google accounts links
                                                     ]) and not any(link.lower().endswith(ext) for ext in ['.pdf', '.ppt', '.pptx'])
                                                    and not re.match(youtube_pattern, link)
                       ]

        #拼接完整url
        base_url = "https://www.google.com"
        for link in links:
            url = urljoin(base_url, link)
            self.logger.info(f'搜索结果url: {url}')

            # 发送一个普通的请求，判断是否为动态网页
            yield Request(url, callback=self.check_dynamic,meta={'keyword':keyword})
        # 打印或保存有效的 URL
        #for url in urls:
            #self.logger.info(f'搜索结果url: {url}')
            #yield {'url': url}
            # 访问每个有效的 结果URL 并调用 parse_article 处理
            #yield scrapy.Request(url, callback=self.parse_article)

            # 限制翻页次数，比如只爬取第一页
        #限制爬取搜索结果页数，每页10条
        page_number = response.meta.get('page_number', 1)  # 获取当前页码

        if  page_number < 20:  # 限制爬取的最大页数
            # 获取下一页的链接
            #next_page = response.css('a#pnnext::attr(href)').get()  # 获取翻页链接（下一页）
            next_page = response.css('a[aria-label="Next page"]::attr(href)').get()
            if next_page:
                # 拼接完整的 URL
                next_page_url = response.urljoin(next_page)
                self.logger.info(f"找到下一页: {next_page_url}")

                # 更新页码并发起请求爬取下一页
                #yield scrapy.Request(next_page_url, callback=self.parse, meta={'page_number': page_number + 1})
                #splash模拟点击翻页
                yield SplashRequest(next_page_url, callback=self.parse, args={'wait': 5},meta={'page_number': page_number + 1,'keyword':keyword})



    #提取搜索结果网页的标题、HTML内容和其他信息
    def parse_article(self, response):

        self.logger.info(f'正在处理文章页面: {response.url}')
        keyword = response.meta.get('keyword')#获取对应关键词

        # 创建 ScrapyCrawlerItem 实例
        item = ScrapyCrawlerItem()

        # 提取标题
        title = response.xpath('//title/text()').get()

        # 提取 HTML 源代码
        html_source = response.text

        # 使用 BeautifulSoup 解析 HTML 内容
        soup = BeautifulSoup(html_source, "html.parser")

        # 获取纯文本，去除所有 HTML 标签
        text1 = soup.get_text()

        # 使用正则表达式替换多个空格为一个空格，并去掉开头和结尾的空格
        text = re.sub(r'\s+', ' ', text1).strip()


        # 提取网页更新时间（如果有）
        last_modified = response.headers.get('Last-Modified', None)  # 获取 HTTP 响应头中的 "Last-Modified" 字段
        if last_modified:
            last_modified = last_modified.decode('utf-8')  # 将字节转换为字符串
        else:
            last_modified = "未知"  # 如果没有提供更新时间

        # 获取爬取的时间（当前时间）
        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


        # 提取语言信息
        # 优先使用 HTTP 响应头中的 Content-Language
        language = response.headers.get('Content-Language', None)
        if language:
            language = language.decode('utf-8').split(',')[0]  # 获取语言字段并去除可能的多种语言设置
        else:
            # 如果没有 Content-Language，检查 HTML 中的 lang 属性
            language = response.css('html::attr(lang)').get()

        # 如果无法从 Content-Language 或 lang 属性获取语言，默认设为 "未知"
        if not language:
            language = "未知"



        # 填充 item
        item['title'] = title
        item['url'] = response.url
        item['last_modified'] = last_modified
        item['crawl_time'] = crawl_time
        item['language'] = language
        item['keyword'] = keyword
        item['source'] = 'google'
        item['text'] = text

        #item['file_path'] = file_path

        # 写入 CSV 文件
        self.write_to_csv(item)
        print(f"{title}已存入csv文件")
        self.logger.debug(f"存入 CSV 的关键词: {item['keyword']}")



        # 返回 item,将 item 传递到pipelines进行存入数据库处理
        #yield item
        return



