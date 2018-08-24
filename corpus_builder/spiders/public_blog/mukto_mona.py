# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class MuktoMonaSpider(CommonSpider):
    name = 'mukto_mona'
    allowed_domains = ['blog.mukto-mona.com']
    base_url = 'https://blog.mukto-mona.com/'
    start_request_url = base_url

    content_body = {
        'css': 'div.post-content p::text'
    }

    rules = (
        Rule(LinkExtractor(
            restrict_css='div.post-content h2.entry-title'
        ),
            callback='parse_content'),
    )

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page']
    ]

    def request_index(self, response):
        for page in range(self.start_page, self.end_page + 1):
            yield scrapy.Request(self.base_url + 'page/{page}/'.format(page=page))
