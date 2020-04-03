# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class HabrBlogSpider(scrapy.Spider):
    name = 'habr_blog'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly/']

    def parse(self, response):
        pagination_urls = response.css('ul.toggle-menu_pagination li a::attr("href")').extract()
        for itm in pagination_urls:
            yield response.follow(itm, callback=self.parse)
        for post_url in response.css('a.post__title_link::attr("href")'):
            yield response.follow(post_url, callback=self.post_parse)


    def post_parse(self, response):
        try:
            tags = response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-tags')]//a/text()").extract()
        except AttributeError as e:
            tags = []


        try:
            hubs = response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-hubs')]//a/text()").extract()
        except AttributeError as e:
            hubs = []

        data = {
            'title': response.xpath("//span[contains(@class, 'post__title-text')]/text()").extract_first(),
            'url': response.url,
            'author-name': response.xpath("//a[contains(@class, 'post__user-info user-info')]//span/text()").extract_first(),
            'authot_url': response.xpath("//a[contains(@class, 'post__user-info user-info')]/@href").extract_first(),
            'post_date': response.xpath("//span[contains(@class, 'post__time')]/text()").extract_first(),
            'tags': tags,
            'hubs': hubs,
            'count_comments': response.xpath("//span[contains(@class, 'post-stats__comments-count')]/text()").extract_first(),
            'date_now': str(datetime.now()),



        }


        yield data




# url tags
#response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-tags')]//a/@href").extract()
# name tags
#response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-tags')]//a/text()").extract()

# url Habs
# response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-hubs')]//a/@href").extract()

# name Habs
# response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-hubs')]//a/text()").extract()





