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
            html_source TEXT,
            last_modified TEXT,
            crawl_time TEXT,
            language TEXT,
            keyword TEXT，
            file_path TEXT
        )
        ''')
    #处理每个爬取到的item
    def process_item(self, item, spider):
        self.cursor.execute('''
                INSERT INTO google_results (title, url, html_source, last_modified, crawl_time, language,keyword)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
            item['title'],
            item['url'],
            item['html_source'],
            item['last_modified'],
            item['crawl_time'],
            item['language'],
            item['keyword'],
            item['file_path']
        ))
        # 提交事务
        self.conn.commit()
        return item

    def close_spider(self, spider):
        '''关闭数据库连接'''
        self.conn.close()
