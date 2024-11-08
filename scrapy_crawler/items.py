# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field()  # 网页标题
    url = scrapy.Field()  # 网页 URL
    html_source = scrapy.Field()  # 网页 HTML 源代码
    last_modified = scrapy.Field()  # 网页更新时间
    crawl_time = scrapy.Field() #爬取时间
    language = scrapy.Field()  # 网页语言（中文或英文）
    keyword = scrapy.Field()#关键词
    file_path = scrapy.Field()#html文件相对路径