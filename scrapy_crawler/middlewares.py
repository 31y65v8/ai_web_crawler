# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from .user_agents import USER_AGENT_LIST
from scrapy_splash import SplashRequest

# useful for handling different item types with a single interface


class ScrapyCrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("启动spider: %s" % spider.name)


class ScrapyCrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        user_agent = random.choice(USER_AGENT_LIST)  # 从列表中随机选择一个 User-Agent
        request.headers['User-Agent'] = user_agent  # 设置请求头中的 User-Agent
        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
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
            splash_url = self.splash_urls[self.index]
            self.index = (self.index + 1) % len(self.splash_urls)  # 更新 index 实现轮询

            # 添加日志输出以确认轮询
            spider.logger.info(f'Using Splash URL: {splash_url}')

            # 设置该请求的 Splash 服务端点
            request.meta['splash']['splash_url'] = splash_url
