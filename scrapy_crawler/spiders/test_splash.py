import scrapy
from scrapy_splash import SplashRequest

class TestSpider(scrapy.Spider):
    name = 'test_spider'

    def start_requests(self):
        urls = [
            'https://www.google.com/search?q=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BDand%E5%8F%91%E5%B1%95%E5%8E%86%E7%A8%8B',
        ]
        for url in urls:
            yield SplashRequest(url, self.parse, args={'wait': 2, 'timeout': 90})

    def parse(self, response):
        title = response.xpath('//title/text()').get()
        self.log(f"Page title: {title}")
