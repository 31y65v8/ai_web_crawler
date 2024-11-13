# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import sqlite3
class GoogleResultPipeline:
    def open_spider(self, spider):
        '''打开数据库连接'''
        self.conn = sqlite3.connect('google_result.db')  # 连接到数据库
        self.cursor = self.conn.cursor()

        # 创建数据库表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS google_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            last_modified TEXT,
            crawl_time TEXT,
            language TEXT,
            keyword TEXT,
            file_path TEXT
        )
        ''')
    #处理每个爬取到的item
    def process_item(self, item, spider):
        if spider.name == "googlespider1":
           self.cursor.execute('''
                INSERT INTO google_results (title, url,  last_modified, crawl_time, language,keyword,file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
            item['title'],
            item['url'],
            item['last_modified'],
            item['crawl_time'],
            item['language'],
            item['keyword'],
            item['file_path']
           ))
          # 提交事务
           self.conn.commit()
           return item
        else:
            return item  # 如果不是 googlespider 的数据，则跳过




    def close_spider(self, spider):
        '''关闭数据库连接'''
        self.conn.close()

class BaiduResultPipeline:
    def open_spider(self, spider):
        '''打开数据库连接'''
        self.conn = sqlite3.connect('baidu_result.db')  # 连接到数据库
        self.cursor = self.conn.cursor()

        # 创建数据库表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS baidu_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            last_modified TEXT,
            crawl_time TEXT,
            language TEXT,
            keyword TEXT,
            file_path TEXT
        )
        ''')
    #处理每个爬取到的item
    def process_item(self, item, spider):
        if spider.name=="baiduspider":
            self.cursor.execute('''
                            INSERT INTO baidu_results (title, url, last_modified, crawl_time, language,keyword,file_path)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                item['title'],
                item['url'],
                item['last_modified'],
                item['crawl_time'],
                item['language'],
                item['keyword'],
                item['file_path']
            ))
            # 提交事务
            self.conn.commit()
            return item

            # 提交事务
            self.conn.commit()
            return item


    def close_spider(self, spider):
        '''关闭数据库连接'''
        self.conn.close()
