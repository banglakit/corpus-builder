# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class CadetCollegeBlogSpider(CommonSpider):
    name = 'cadet_college_blog'
    allowed_domains = ['www.cadetcollegeblog.com', 'cadetcollegeblog.com']
    base_url = 'http://www.cadetcollegeblog.com/'
    start_request_url = base_url

    content_body = {
        'css': 'div.entry-content p::text'
    }

    rules = (
        Rule(LinkExtractor(
            restrict_css='article h2'
        ),
            callback='parse_content'),
    )

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page']
    ]

    def request_index(self, response):
        for page in range(self.start_page, self.end_page + 1):
            yield scrapy.Request(self.base_url + 'page/{page}'.format(page=page))
