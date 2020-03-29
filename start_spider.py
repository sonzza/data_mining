from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from blogparse import settings
from blogparse.spiders.gb_blog import GbBlogSpider
from blogparse.spiders.habrhabr import HabrhabrSpider


if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)
    # crawler_proc.crawl(GbBlogSpider)
    crawler_proc.crawl(HabrhabrSpider)
    crawler_proc.start()
