# -*- coding: utf-8 -*-
import datetime

import dateutil.parser
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry


class SamakalSpider(CrawlSpider):
    name = "samakal"
    allowed_domains = ["bangla.samakal.net"]

    rules = (
        Rule(
            LinkExtractor(
                # http://bangla.samakal.net/2016/06/01/215743
                allow=('/\d{4}/\d{2}/\d{2}/\d+$'),
                restrict_xpaths=('//div[@class="main-body"]')
            ),
            callback='parse_news'),
    )

    def __init__(self, start_date=None, end_date=None, *a, **kw):
        self.start_date = dateutil.parser.parse(start_date)
        self.end_date = dateutil.parser.parse(end_date)

        self.categories = []

        super(SamakalSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('http://bangla.samakal.net/',
                             callback=self.start_categorized_requests)

    def start_categorized_requests(self, response):
        self.categories = list(set(response.css('#topMenuItem a::attr("href")').re('/([^\/]+)/$')))

        if not self.categories:
            raise ValueError('No categories found')

        date_processing = self.start_date
        while date_processing <= self.end_date:
            for category in self.categories:
                # redifining the rule again according to the specific date url
                SamakalSpider.rules = (Rule(LinkExtractor(allow=('/' + date_processing.strftime('%Y/%m/%d') + '/\d+$',),
                                                          restrict_xpaths=('//div[@class="main-body"]')),
                                            callback="parse_news", follow=True),)
                super(SamakalSpider, self)._compile_rules()
                # http://bangla.samakal.net/-education/2016/06/01 
                url = 'http://bangla.samakal.net/{0}/{1}'.format(
                    category,
                    date_processing.strftime('%Y/%m/%d')
                )
                yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(part for part in response.css('div#newsDtl *::text').extract())
        return item
