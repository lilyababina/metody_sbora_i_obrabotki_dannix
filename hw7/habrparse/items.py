# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


class HabrparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def clean_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values

class AvitoRealEstateItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(clean_photo))

class ZillowItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    sqft = scrapy.Field()