# -*- coding: utf-8 -*-
import scrapy
import datetime

import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry


class NewspaperSpider(CrawlSpider):
    def __init__(self, start_date=None, end_date=None, start_page=None, end_page=None, archive=False,
        category=None, subcategory=None, *a, **kw):

        # get local variables, delete some
        args = locals()
        del args['a']
        del args['kw']
        del args['self']

        user_configuration = []
        valid_config = False

        # construct user's configuration
        for key, value in args.iteritems():
            if value:
                user_configuration.append(key)

        # compare with allowed configurations
        for configuration in self.allowed_configurations:
            if sorted(configuration) == sorted(user_configuration):
                valid_config = True
                break

        if not valid_config:
            raise ValueError('combination of ({0}) not allowed'.format(", ".join(user_configuration)))

        self.start_page = int(start_page) if start_page else None
        self.end_page = int(end_page) if end_page else self.start_page
        self.start_date = dateutil.parser.parse(start_date) if start_date else None
        self.end_date = dateutil.parser.parse(end_date) if end_date else self.start_date

        self.archive = bool(archive)
        self.category = category
        self.subcategory = subcategory

        super(NewspaperSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request(self.start_request_url, callback=self.request_index)

    def parse_news(self, response):
        item = TextEntry()

        if self.news_body.get('xpath'):
            article_text_children = response.xpath(self.news_body.get('xpath')).extract()
        elif self.news_body.get('css'):
            article_text_children = response.css(self.news_body.get('css')).extract()
        else:
            raise NotImplementedError('text extraction selector underfined')

        item['body'] = "".join(child for child in article_text_children)
        return item