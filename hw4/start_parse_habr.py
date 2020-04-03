from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from habrparse.spiders.habr_blog import HabrBlogSpider
from habrparse import settings

if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)
    crawler_proc.crawl(HabrBlogSpider)
    crawler_proc.start()