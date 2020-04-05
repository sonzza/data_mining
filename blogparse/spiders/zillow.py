# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
import re
from blogparse.items import ZillowItem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/homes/Florence,-AL_rb/']
    browser = webdriver.Firefox()



    def parse(self, response):
        for pag_url in response.xpath('//nav[@aria-label="Pagination"]/ul/li/a/@href'):
            yield response.follow(pag_url, callback=self.parse)

        for ads_url in response.xpath('//ul[contains(@class, "photo-cards_short")]/li/article/div['
                                      '@class="list-card-info"]/a/@href'):

            yield response.follow(ads_url, callback=self.ads_parse)

    def ads_parse(self, response):
        item = ItemLoader(ZillowItem(), response)
        self.browser.get(response.url)
        media_col = self.browser.find_element_by_css_selector('div.ds-media-col')
        photo_pic_len = len(self.browser.find_elements_by_xpath('//ul[@class="media-stream"]/li/picture/source['
                                                                '@type="image/jpeg"]'))
        while True:
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            tmp = len(self.browser.find_elements_by_xpath('//ul[@class="media-stream"]/li/picture/source['
                                                                '@type="image/jpeg"]'))
            if tmp == photo_pic_len:
                break
            photo_pic_len = tmp
        images = [itm.get_attribute('srcset').split(' ')[-2] for itm in self.browser.find_elements_by_xpath(
            '//ul[@class="media-stream"]/li/picture/source[@type="image/jpeg"]')]
        item.add_value('photos', images)
        item.add_value('url', response.url)
        item.add_value('title', re.findall("\d+_zpid", response.url))
        item.add_value('price', self.browser.find_element_by_xpath('//*[@id="ds-container"]//h3/span').text)
        item.add_value('address', self.browser.find_element_by_xpath('//*[@id="ds-container"]//h1/span').text)
        item.add_value('sqft', [itm.text for itm in self.browser.find_elements_by_class_name('ds-bed-bath-living-area')][-4])
        yield item.load_item()



