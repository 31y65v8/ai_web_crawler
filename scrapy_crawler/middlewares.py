from scrapy import signals
import random
from .user_agents import USER_AGENT_LIST
from scrapy_splash import SplashRequest
'''coded by 王栩麓'''
class ScrapyCrawlerSpiderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):

        return None

    def process_spider_output(self, response, result, spider):

        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):

        pass

    def process_start_requests(self, start_requests, spider):

        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("启动spider: %s" % spider.name)


class ScrapyCrawlerDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):

        user_agent = random.choice(USER_AGENT_LIST)  # 从列表中随机选择一个 User-Agent
        request.headers['User-Agent'] = user_agent  # 设置请求头中的 User-Agent

        return None

    def process_response(self, request, response, spider):

        return response

    def process_exception(self, request, exception, spider):

        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


'''class ProxyMiddleware:
    def __init__(self):
        self.proxy_url = "http://127.0.0.1:5010/get"  # jhao104 的代理池地址

    def get_random_proxy(self):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                return response.text
        except requests.ConnectionError:
            return None

    def process_request(self, request, spider):
        proxy = self.get_random_proxy()
        if proxy:
            request.meta["proxy"] = "http://" + proxy'''
class SplashProxyMiddleware:
    def __init__(self, splash_urls):
        self.splash_urls = splash_urls
        self.index = 0  # 轮询计数器
    @classmethod
    def from_crawler(cls, crawler):
        spider = crawler.spider
        spider.logger.info("SplashProxyMiddleware initialized")
        return cls(splash_urls=crawler.settings.get('SPLASH_URLS'))

    def process_request(self, request, spider):
        # 只对 SplashRequest 类型的请求进行负载均衡
        if isinstance(request, SplashRequest):
            '''# 随机选择一个 Splash 实例
            splash_url = random.choice(self.splash_urls)
            # 设置 Splash URL
            request.meta['splash']['endpoint'] = splash_url'''
            # 获取当前的 Splash URL 并更新 index
            #splash_url = self.splash_urls[self.index]
            #self.index = (self.index + 1) % len(self.splash_urls)  # 更新 index 实现轮询
            splash_url = random.choice(['http://localhost:8050', 'http://localhost:8051'])#随机分配

            # 添加日志输出以确认轮询
            spider.logger.info(f'Using Splash URL: {splash_url}')

            # 设置该请求的 Splash 服务端点
            request.meta['splash']['splash_url'] = splash_url
