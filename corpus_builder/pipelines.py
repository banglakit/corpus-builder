# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem


class StripPipeline(object):
    def process_item(self, item, spider):
        if item['body']:
            item['body'] = item['body'].strip()
            return item
        else:
            raise DropItem("Empty Body")