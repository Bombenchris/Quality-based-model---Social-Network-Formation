# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FollowersItem(scrapy.Item):
    # define the fields for your item here like:
    GAME = scrapy.Field()
    ID = scrapy.Field()
    USER = scrapy.Field()
    FOLLOWERS = scrapy.Field()
    view_count = scrapy.Field()

    created_at = scrapy.Field()
    updated_at = scrapy.Field()

    gaming_hour = scrapy.Field()
    total_hour = scrapy.Field()
    dedication = scrapy.Field()

    pass
