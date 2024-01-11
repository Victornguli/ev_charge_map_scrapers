# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZapMapRawPoint(scrapy.Item):
    token = scrapy.Field(serializer=str)
    legacy_id = scrapy.Field(serializer=int)
    uuid = scrapy.Field(serializer=str)
    created_at = scrapy.Field(serializer=str)


class ZapMapFinalPoint(scrapy.Item):
    pass
