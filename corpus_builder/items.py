# -*- coding: utf-8 -*-

import scrapy


class TextEntry(scrapy.Item):
    """the corpus entry type"""
    body = scrapy.Field()
