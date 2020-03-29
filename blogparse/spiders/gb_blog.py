# -*- coding: utf-8 -*-
import scrapy


class GbBlogSpider(scrapy.Spider):
    name = 'gb_blog'
    allowed_domains = ['geekbrains.ru']
    start_urls = ['https://geekbrains.ru/posts']

    def parse(self, response):
        pagination_urls = response.css('ul.gb__pagination li a::attr("href")').extract()
        for itm in pagination_urls:
            yield response.follow(itm, callback=self.parse)

        for post_url in response.css('a.post-item__title::attr("href")'):
            yield response.follow(post_url, callback=self.post_parse)

    def poszt_parse(self, response):
        try:
            tags = response.xpath("//article//i[contains(@class, 'i-tag')]/@keywords").extract_first().split(', ')
        except AttributeError as e:
            tags = []
        data = {
            'title': response.css('h1.blogpost-title::text').extract_first(),
            'url': response.url,
            'tags': tags,
        }

        yield data

    def tag_parse(self, response, data):
        print(1)
