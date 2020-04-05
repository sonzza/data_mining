# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class BlogparsePipeline(object):
    def __init__(self):
        client = MongoClient('mongodb://localhost:27017/')
        self.db = client['blog_parse']

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item


class ImgPipeLine(ImagesPipeline):

    def get_media_requests(self, item, info):

        if item.get('photos'):
            for img_url in item['photos']:
                try:
                    yield scrapy.Request(img_url)
                except Exception as e:
                    pass

    def item_completed(self, results, item, info):
        if results:
            item['url'] = item['url'][0]
            item['title'] = item['title'][0]
            item['price'] = item['price'][0]
            item['address'] = item['address'][0]
            item['square'] = item['sqft'][0]
            item['photos'] = [itm[1] for itm in results]
            # item['autor'] = item['autor'].strip()
            # item['flat_params'] = item['flat_params'][0]
            # item['public_date'] = item['public_date'].strip()
            # item['autor_url'] = f'http://avito.ru{item["autor_url"]}'
        return item




class TempPipeline:
    def process_item(self, item, spider):
        return item
