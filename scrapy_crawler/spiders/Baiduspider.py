import scrapy
import os
import re
from urllib.parse import urlencode, urljoin
from datetime import datetime
from scrapy_splash import SplashRequest
from scrapy import Request
from scrapy_crawler.items import ScrapyCrawlerItem

def create_baidu_url(query, site=''):  # 构建百度搜索的URL
    baidu_dict = {'wd': query, 'rn': 10}  # 查询词和每页结果数量
    if site:
        baidu_dict['site'] = site
    return 'https://www.baidu.com/s?' + urlencode(baidu_dict)

class BaiduSpiderSpider(scrapy.Spider):
    keyword = ""
    name = "baiduspider"
    start_urls = ['http://baidu.com']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'CONCURRENT_REQUESTS': 2,
        'RETRY_TIMES': 3,
        'DOWNLOAD_DELAY': 3,
        'RETRY_HTTP_CODES': [502, 503, 504, 408],
        'RANDOMIZE_DOWNLOAD_DELAY': True
    }

    base_queries = ['人工智能应用']
    extension_queries = ['行业']
    combined_queries = []

    def start_requests(self):
        for base in self.base_queries:
            for extension in self.extension_queries:
                query = f"{base} {extension}"
                self.combined_queries.append(query)

        for query in self.combined_queries:
            self.logger.debug(f"正在查询关键词: {query}")
            self.keyword = query
            url = create_baidu_url(query)
            yield SplashRequest(
                url,
                callback=self.parse,
                args={'wait': 5},
                endpoint='render.html'
            )

        # 判断是否为动态网页
    def is_dynamic(self, html_source):
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
    def check_dynamic(self, response):
        if self.is_dynamic(response.text):
            # 如果是动态网页，使用 Splash 渲染页面,再调用 parse_article
            self.logger.info(f"动态网页: {response.url}，使用 Splash 渲染")
            yield SplashRequest(response.url, self.parse_article, args={'wait': 6})
        else:
            # 如果不是动态网页，直接调用 parse_article
            self.logger.info(f"静态网页: {response.url}，直接解析")
            yield self.parse_article(response)

    def parse(self, response):
        self.logger.debug(f"响应状态码: {response.status}")

        if response.status != 200:
            self.logger.error(f"请求失败，状态码: {response.status} ， URL: {response.url}")
            return  # 如果请求失败，跳过

        # 提取百度搜索结果页面中的 URL
        urls = response.css('div.c-span3 a::attr(href)').getall()  # 提取所有匹配的链接

        self.logger.debug(f'匹配到的搜索结果URL数: {len(urls)}')  # 输出匹配到的链接数量

        # 去除无效链接，排除百度学术（xueshu.baidu.com）和其他无关的 URL
        valid_urls = [
            url.split('&')[0]  # 去掉无关参数
            for url in urls
            if not any(x in url for x in [
                'xueshu.baidu.com',  # 排除百度学术网址

            ])
        ]

        # 拼接完整url并输出有效的 URL
        base_url = "https://www.baidu.com"
        for url in valid_urls:
            full_url = urljoin(base_url, url)
            self.logger.info(f'有效的搜索结果url: {full_url}')

            # 发送请求处理每个有效链接
            yield scrapy.Request(full_url, callback=self.check_dynamic)

        # 限制翻页次数，比如只爬取第一页
        page_number = response.meta.get('page_number', 1)  # 获取当前页码
        if page_number < 2:  # 限制爬取的最大页数（这里是5页）
            # 获取“下一页”的链接
            next_page = response.css('a.n::attr(href)').get()
            if next_page:
                # 拼接完整的 URL
                next_page_url = response.urljoin(next_page)
                self.logger.info(f"找到下一页: {next_page_url}")

                # 更新页码并发起请求爬取下一页
                yield SplashRequest(next_page_url, callback=self.parse, args={'wait': 5},
                                    meta={'page_number': page_number + 1})

    def parse_article(self, response):
        item = ScrapyCrawlerItem()
        # 提取标题
        title = response.xpath('//title/text()').get()
        html_source = response.text
        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        folder_path = 'Baidu'+'-'.join(self.combined_queries)
        os.makedirs(folder_path, exist_ok=True)
        filename = f"{title}.txt".replace(" ", "_").replace(":", "_").replace("/", "_")
        filename = filename.replace("\\", "_").replace("?", "_").replace("*", "_")
        file_path = os.path.join(folder_path, filename)

        if os.path.exists(file_path):
            print(f"文件 '{file_path}' 已存在，跳过保存和数据库存储。")
            return

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_source)

        language = response.headers.get('Content-Language', None)
        if language:
            language = language.decode('utf-8').split(',')[0]
        else:
            language = response.css('html::attr(lang)').get() or "未知"

        item['title'] = title
        item['url'] = response.url
        item['crawl_time'] = crawl_time
        item['language'] = language
        item['keyword'] = self.keyword
        item['file_path'] = file_path

        yield item
