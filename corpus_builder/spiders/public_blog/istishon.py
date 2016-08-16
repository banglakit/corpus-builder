# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class IstishonSpider(CommonSpider):
    name = 'istishon'
    allowed_domains = ['www.istishon.com']
    base_url = 'http://www.istishon.com'
    start_request_url = base_url + '/blog'

    content_body = {
        'css': 'div.content p::text'
    }

    rules = (
        Rule(LinkExtractor(
            restrict_css='div.content h2'
        ),
            callback='parse_content'),
    )

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page']
    ]

    def request_index(self, response):
        for page in range(self.start_page, self.end_page + 1):
            yield scrapy.Request(self.base_url + '/?q=node&page={page}'.format(page=page))
