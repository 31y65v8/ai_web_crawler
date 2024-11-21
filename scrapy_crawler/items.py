import scrapy
'''coded by 王栩麓'''
class ScrapyCrawlerItem(scrapy.Item):

    title = scrapy.Field()  # 网页标题
    url = scrapy.Field()  # 网页 URL
    text = scrapy.Field()  # 网页文本内容
    last_modified = scrapy.Field()  # 网页更新时间
    crawl_time = scrapy.Field() #爬取时间
    language = scrapy.Field()  # 网页语言（中文或英文）
    keyword = scrapy.Field()#关键词
    source = scrapy.Field()#网页来源
    #file_path = scrapy.Field()#html文件相对路径