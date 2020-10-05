# -*- coding: utf-8 -*-

# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Document(scrapy.Item):
    title = scrapy.Field()
    text = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    edition = scrapy.Field()
    topics = scrapy.Field()
    authors = scrapy.Field()
    reposts_fb = scrapy.Field()
    reposts_vk = scrapy.Field()
    reposts_ok = scrapy.Field()
    reposts_twi = scrapy.Field()
    reposts_lj = scrapy.Field()
    reposts_tg = scrapy.Field()
    likes = scrapy.Field()
    views = scrapy.Field()
    comm_count = scrapy.Field()
