# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class BigganProjuktiSpider(CommonSpider):
    name = 'biggan_projukti'
    allowed_domains = ['www.bigganprojukti.com', 'bigganprojukti.com']
    base_url = 'http://www.bigganprojukti.com/'
    start_request_url = base_url

    content_body = {
        'css': 'div.td-post-content p::text'
    }

    rules = (
        Rule(LinkExtractor(
            restrict_css='div.td-main-content h3.entry-title'
        ),
            callback='parse_content'),
    )

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page']
    ]

    def request_index(self, response):
        for page in range(self.start_page + 1, self.end_page + 1):
            yield scrapy.Request(self.base_url + 'page/{page}'.format(page=page))
