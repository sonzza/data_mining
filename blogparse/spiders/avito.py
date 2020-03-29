import scrapy
from scrapy.loader import ItemLoader
from blogparse.items import AvitoRealEstateItem

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru', 'avito.ru']
    start_urls = ['https://www.avito.ru/sankt-peterburg/kvartiry/']

    def parse(self, response):
        for num in response.xpath('//div[@data-marker="pagination-button"]//span/text()'):
            try:
                tmp = int(num.get())
                yield response.follow(f'/sankt-peterburg/kvartiry/?p={tmp}', callback=self.parse)
            except TypeError as e:
                continue
            except ValueError as e:
                continue

        for ads_url in response.css('div.item_table h3.snippet-title a.snippet-link::attr("href")'):
            yield response.follow(ads_url, callback=self.ads_parse)

    def ads_parse(self, response):
        item = ItemLoader(AvitoRealEstateItem(), response)
        item.add_value('url', response.url)
        item.add_css('title', 'div.title-info-main h1.title-info-title span::text')
        item.add_css('public_date', 'div.title-info-metadata-item-redesign::text')
        item.add_css('autor', 'div.seller-info-name a::text')
        item.add_css('autor_url', 'div.seller-info-name a::attr("href")')
        item.add_css('flat_params', 'ul li.item-params-list-item ::text')
        item.add_xpath('photos', "//div[contains(@class, 'gallery-img-frame')]/@data-url")
        yield item.load_item()
