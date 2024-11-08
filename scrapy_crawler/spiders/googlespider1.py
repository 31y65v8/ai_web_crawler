import scrapy
import os
import re
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urljoin
from datetime import datetime
from scrapy_crawler.items import ScrapyCrawlerItem
from scrapy_splash import SplashRequest
from scrapy import Request

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
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'RETRY_TIMES': 3,
        'DOWNLOAD_DELAY': 2  # 限制请求之间的延迟时间，防止过于频繁的请求
        , 'RETRY_HTTP_CODES': [502, 503, 504, 408],
        'RANDOMIZE_DOWNLOAD_DELAY' : True  # 启用请求延迟的随机化

    }

    # 创建数据库连接并初始化表
    #def __init__(self, *args, **kwargs):
     #   super().__init__(*args, **kwargs)
        # 连接 SQLite 数据库
      #  self.conn = sqlite3.connect('web_data.db')
       # self.cursor = self.conn.cursor()
        # 创建数据表
        #self.cursor.execute('''CREATE TABLE IF NOT EXISTS g_test_webpages (
                                           #id INTEGER PRIMARY KEY AUTOINCREMENT,
                                           #title TEXT,
                                           #html_file_path TEXT,
                                           #link TEXT,
                                           #position INTEGER,
                                           #date TEXT
                                         #)''')
    # 基础关键词
    base_queries = ['人工智能发展路径','人工智能发展史','人工智能发展历程','AI发展路径','AI发展史','AI发展历程']

    # 拓展关键词
    extension_queries = [
        '三个阶段',
        '大事记',
        '三起两落',
        '典型技术',
        '典型事件'
    ]
    # 组合生成查询
    combined_queries = []

    def start_requests(self):
        '''headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',  # 增加 Accept-Language 头，模拟更真实的浏览器行为
            'Accept-Encoding': 'gzip, deflate, br'
        }'''

        '''# 中文基础关键词
        ch_base_queries = ['人工智能']

        # 中文拓展关键词
        ch_extension_queries = [
            '应用',
            '影响行业'
        ]
        # 中文组合生成查询
        ch_combined_queries = []'''

        for base in self.base_queries:
            for extension in self.extension_queries:
                query = f"{base} AND {extension}"
                self.combined_queries.append(query)

        # 发送请求到每个查询
        for query in self.combined_queries:
            self.logger.debug(f"正在查询关键词: {query}")  # 打印当前正在处理的查询
            self.keyword = query#在数据库中标记关键词字段
            url = create_google_url(query)  # 创建 Google 搜索的 URL
            #yield scrapy.Request(url, callback=self.parse)
            #Google搜索结果页为动态页面，使用splash加载动态页面（先打开docker）
            yield SplashRequest(
                url,
                callback=self.parse,
                args={'wait': 5},  # 等待时间，确保页面加载完成
                endpoint='render.html',
            )

            '''# 随机等待 1 到 3 秒之间的时间
            time.sleep(random.uniform(3, 5))
'''
    '''
    #爬取每个搜索结果的html
    def parse_search_results(self, response):
            self.logger.debug(f"正在解析网页： {response.url}")

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

    '''

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
        if self.is_dynamic(response.text):
            # 如果是动态网页，使用 Splash 渲染页面,再调用 parse_article
            self.logger.info(f"动态网页: {response.url}，使用 Splash 渲染")
            yield SplashRequest(response.url, self.parse_article, args={'wait': 6})
        else:
            # 如果不是动态网页，直接调用 parse_article
            self.logger.info(f"静态网页: {response.url}，直接解析")
            yield self.parse_article(response)



    #爬取搜索结果页，获取每个搜索结果的url列表
    def parse(self, response):
        self.logger.debug(f"响应状态码: {response.status}")

        if response.status != 200:
            self.logger.error(f"请求失败，状态码: {response.status} ， URL: {response.url}")
            return  # 如果请求失败，跳过

        '''# 输出渲染后的 HTML 内容
        rendered_html = response.text  # 获取渲染后的 HTML
        self.logger.debug(f"渲染后的 HTML 内容:\n{rendered_html}")'''



        # 使用正则表达式查找所有链接,返回一个包含所有匹配url的列表
        # 匹配带有 jsname="UWckNb" 的链接，这包含搜索结果网页的url，观察搜索结果页面html分析得出（不包含谷歌学术论文）
        #urls = re.findall(r'<a[^>]*jsname="UWckNb"[^>]*href="(https?://[^"]+)"', response.text)

        # 使用正则表达式查找所有链接,返回一个包含所有匹配links的列表（不是完整url）
        # 提取 <div class="egMi0 kCrY T"> 内的 href 属性，这包含搜索结果网页的link，观察搜索结果页面html分析得出（不包含谷歌学术论文）
        links = response.xpath('//div[contains(@class, "egMi0") and contains(@class, "kCrY")]/a/@href').extract()
        self.logger.debug(f'匹配到的搜索结果URL数: {len(links)}')  # 输出匹配到的链接数量


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
                                                    'accounts.google.com'])  # Google accounts links
                      ]

        #拼接完整url
        base_url = "https://www.google.com"
        for link in links:
            url = urljoin(base_url, link)
            self.logger.info(f'搜索结果url: {url}')

            # 发送一个普通的请求，判断是否为动态网页
            yield Request(url, callback=self.check_dynamic)
        # 打印或保存有效的 URL
        #for url in urls:
            #self.logger.info(f'搜索结果url: {url}')
            #yield {'url': url}
            # 访问每个有效的 结果URL 并调用 parse_article 处理
            #yield scrapy.Request(url, callback=self.parse_article)

            # 限制翻页次数，比如只爬取第一页
        #限制爬取搜索结果页数，每页10条
        page_number = response.meta.get('page_number', 1)  # 获取当前页码

        if page_number < 20:  # 限制爬取的最大页数（这里是20页）
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
                yield SplashRequest(next_page_url, callback=self.parse, args={'wait': 5},meta={'page_number': page_number + 1})



    #提取搜索结果网页的标题、HTML内容和其他信息
    def parse_article(self, response):

        self.logger.info(f'正在处理文章页面: {response.url}')

        # 创建 ScrapyCrawlerItem 实例
        item = ScrapyCrawlerItem()

        # 提取标题
        title = response.xpath('//title/text()').get()

        # 提取 HTML 源代码
        html_source = response.text

        # 提取网页更新时间（如果有）
        last_modified = response.headers.get('Last-Modified', None)  # 获取 HTTP 响应头中的 "Last-Modified" 字段
        if last_modified:
            last_modified = last_modified.decode('utf-8')  # 将字节转换为字符串
        else:
            last_modified = "未知"  # 如果没有提供更新时间

        # 获取爬取的时间（当前时间）
        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 创建一个文件夹存储 HTML 文件
        #folder_path = 'test'
        folder_path = '-'.join(self.combined_queries)
        os.makedirs(folder_path, exist_ok=True)
        print(f"文件夹 '{folder_path}' 创建成功")

        # 生成 HTML 文件名（避免特殊字符）
        filename = f"{title}.txt".replace(" ", "_").replace(":", "_").replace("/", "_")
        filename = filename.replace("\\", "_").replace("?", "_").replace("*", "_")
        filename = filename.replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
        # 文件路径
        file_path = os.path.join(folder_path, filename)

        #简单的判重：标题相同的网页只存储一次
        if os.path.exists(file_path):
            print(f"文件 '{file_path}' 已存在，跳过保存和数据库存储。")
            return

        # 保存 HTML 到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_source)

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
        item['html_source'] = html_source
        item['last_modified'] = last_modified
        item['crawl_time'] = crawl_time
        item['language'] = language
        item['keyword'] = self.keyword
        item['file_path'] = file_path

        # 返回 item,将 item 传递到pipelines进行存入数据库处理
        yield item

    '''# 打印返回的 HTML 内容，查看是否包含验证码或者其他异常页面
    self.logger.debug(f"Response content: {response.text[:1000]}")  # 打印前 1000 个字符
    '''

    ''' # 直接获取并保存 HTML 内容
        html_content = response.text
        #title = response.xpath('//title/text()').get()  # 从网页中提取标题
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')'''

    '''
        # 创建目录存放 HTML 文件
        os.makedirs('html_files', exist_ok=True)
        file_name = f'html_files/{title}_{dt}.html'.replace(" ", "_").replace(":", "_").replace("/", "_")

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f"Saved HTML file at: {file_name}")

        # 你可以选择将 HTML 内容保存到数据库或者进行其他处理'''

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
    '''


