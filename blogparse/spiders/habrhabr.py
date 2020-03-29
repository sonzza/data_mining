# -*- coding: utf-8 -*-
import scrapy


class HabrhabrSpider(scrapy.Spider):
    name = 'habrhabr'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly/']

    def parse(self, response):
        pagination_urls = response.xpath('//*[@id="next_page"]/@href')
        for itm in pagination_urls:
            yield response.follow(itm, callback=self.parse)

        for post_url in response.xpath('//a[contains(@class,"post__title_link")]/@href'):
            yield response.follow(post_url, callback=self.post_parse)

    def post_parse(self, response):
        try:
            tags = response.css('ul.js-post-tags a.post__tag::text').extract()
        except AttributeError as e:
            tags = []
        try:
            hubs = response.css('ul.js-post-hubs a.post__tag::text').extract()
            for i in range(len(hubs)):
                hubs[i] = hubs[i].strip()
        except AttributeError as e:
            hubs = []
        try:
            comment_writers = [{'name': item.xpath('@data-user-login').extract(), 'url': item.xpath('@href').extract()}
                               for item in response.css('a.user-info_inline')]
        except AttributeError as e:
            comment_writers = {}
        data = {
            'title': response.css('span.post__title-text::text').extract_first(),
            'url': response.url,
            'writer': {'name': response.css(
                'article.post header.post__meta a.post__user-info span.user-info__nickname::text').extract_first(),
                       'url': response.css(
                           'article.post header.post__meta a.post__user-info::attr("href")').extract_first()
                       },
            'pub_date': response.css(
                'article.post header.post__meta span.post__time::attr("data-time_published")').extract_first(),
            'comment_count': response.css('span.post-stats__comments-count::text').extract_first(),
            'comment_writers': comment_writers,
            'tags': tags,
            'hubs': hubs
        }

        yield data
