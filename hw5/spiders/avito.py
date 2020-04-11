# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from habrparse.items import AvitoRealEstateItem

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru', 'www.avito.ru']
    start_urls = ['https://www.avito.ru/moskva/kvartiry/']

    def parse(self, response):
        for num in response.xpath('//div[@data-marker="pagination-button"]//span/text()'):
            try:
                tmp = int(num.get())
                yield response.follow(f'/moskva/kvartiry/?p={tmp}', callback=self.parse)

            except TypeError as e:
                continue
            except ValueError as e:
                continue


        for ads_url in response.css('div.item_table h3.snippet-title a.snippet-link::attr("href")'):
            yield response.follow(ads_url, callback=self.ads_parse)

    def ads_parse(self, response):
        item = ItemLoader(AvitoRealEstateItem(),response)
        item.add_value('url', response.url)
        item.add_css('title', 'div.title-info-main h1.title-info-title span::text')
        item.add_xpath('photos', "//div[contains(@class, 'gallery-img-frame')]/@data-url")
        item.add_value('floor_number', response.xpath("//span[text()='Этаж: ']/parent::li/text()").extract()[1])
        item.add_value('floors_in_house', response.xpath("//span[text()='Этажей в доме: ']/parent::li/text()").extract()[1])
        item.add_value('type_of_house', response.xpath("//span[text()='Тип дома: ']/parent::li/text()").extract()[1])
        item.add_value('rooms_count', response.xpath("//span[text()='Количество комнат: ']/parent::li/text()").extract()[1])
        item.add_value('square', response.xpath("//span[text()='Общая площадь: ']/parent::li/text()").extract()[1])
        item.add_value('living_square', response.xpath("//span[text()='Жилая площадь: ']/parent::li/text()").extract()[1])
        item.add_value('square_of_kitchen', response.xpath("//span[text()='Площадь кухни: ']/parent::li/text()").extract()[1])
        item.add_value('time_publish', response.xpath("//div[contains(@class, 'title-info-metadata-item-redesign')]/text()").extract()[0])
        item.add_value('name', response.xpath("//div[contains(@class, 'seller-info-name js-seller-info-name')]/a/text()").extract()[0])
        item.add_value('name_url', response.xpath("//div[contains(@class, 'seller-info-name js-seller-info-name')]/a/@href").extract()[0])



        yield item.load_item()



#этаж
#этажей в доме
#тип дома-монолитный
#количество комнат-двухкомнатные
#общая площадь 60 м2
#площадь кухни 15 м2
#Задание:
#Источник: https://www.avito.ru/ раздел недвижимость квартиры
#Извлекаем слуд параметры:
#- заголовок
#- url объявления
#- дата публикации
#- все фото
#- имя и ссылка на автора объявления
#- список параметров объявления из этого блока (https://www.dropbox.com/s/e1dho7iwom93fnb/%D0%A1%D0%BA%D1%80%D0%B8%D0%BD%D1%88%D0%BE%D1%82%202020-03-26%2022.11.42.png?dl=0)
#- телефон если получится
#обязательно использовать Item и ItemLoader