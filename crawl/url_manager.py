#1.起始url池、url管理
# url_manager.py
'''
url从搜索引擎中获取，主要通过在搜索引擎中搜索人工智能相关关键词来提取搜索结果中的url
搜索引擎：
主要：
Google、Bing、Baidu、Sogou（搜狗）
辅助：
Yahoo、DuckDuckGo、360
'''

class URLManager:
    def __init__(self):
        # 初始化两个集合，一个用于存储待爬取的 URL，另一个存储已爬取的 URL
        self.new_urls = set()  # 待爬取的 URL 集合
        self.crawled_urls = set()  # 已爬取的 URL 集合

    def add_url(self, url):
        """
        添加单个 URL 到待爬取集合中
        :param url: 需要添加的 URL
        """
        if url is None:
            return
        if url not in self.new_urls and url not in self.crawled_urls:
            self.new_urls.add(url)

    def add_urls(self, urls):
        """
        批量添加 URL 到待爬取集合中
        :param urls: 需要添加的 URL 列表或集合
        """
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_url(url)

    def get_next_url(self):
        """
        获取一个待爬取的 URL，并将其从待爬取集合移动到已爬取集合中
        :return: 下一个待爬取的 URL
        """
        if self.has_new_url():
            next_url = self.new_urls.pop()
            self.crawled_urls.add(next_url)
            return next_url
        return None

    def has_new_url(self):
        """
        判断是否还有待爬取的 URL
        :return: 如果有待爬取的 URL，返回 True，否则返回 False
        """
        return len(self.new_urls) > 0

    def get_new_url_count(self):
        """
        获取待爬取 URL 的数量
        :return: 待爬取 URL 的数量
        """
        return len(self.new_urls)

    def get_crawled_url_count(self):
        """
        获取已爬取 URL 的数量
        :return: 已爬取 URL 的数量
        """
        return len(self.crawled_urls)

    def is_crawled(self, url):
        """
        检查某个 URL 是否已经被爬取过
        :param url: 需要检查的 URL
        :return: 如果 URL 已被爬取，返回 True，否则返回 False
        """
        return url in self.crawled_urls
