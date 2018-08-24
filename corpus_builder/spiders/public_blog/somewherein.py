# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class SomewhereInSpider(CommonSpider):
    name = 'somewherein'
    allowed_domains = ['www.somewhereinblog.net', 'somewhereinblog.net']
    base_url = 'http://www.somewhereinblog.net/'
    start_request_url = base_url

    content_body = {
        'css': '.blog-content::text'
    }

    rules = (
        Rule(LinkExtractor(
            restrict_css='h2.post-title'
        ),
            callback='parse_content'),
    )

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page']
    ]

    def request_index(self, response):
        for page in range(self.start_page - 1, self.end_page ):
            yield scrapy.Request(self.base_url + 'live/{page}'.format(page=page * 15))
