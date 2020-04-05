from dotenv import load_dotenv
from pathlib import Path
import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from blogparse import settings
from blogparse.spiders.gb_blog import GbBlogSpider
from habrparse.spiders.avito import AvitoSpider
from habrparse.spiders.instagram import InstagramSpider
from habrparse.spiders.instagram import InstagramSpider_2

env_path = Path(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)




if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings = craw_settings)
    #crawler_proc.crawl(GbBlogSpider)
    #crawler_proc.crawl(AvitoSpider)
    crawler_proc.crawl(InstagramSpider, logpass=(os.getenv('INSTA_LOGIN'), os.getenv('INSTA_PWD')))
    crawler_proc.crawl(InstagramSpider_2, logpass=(os.getenv('INSTA_LOGIN'), os.getenv('INSTA_PWD')))

    crawler_proc.start()
