# -*- coding: utf-8 -*-
import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class SamakalSpider(CommonSpider):
    name = "samakal"
    allowed_domains = ["bangla.samakal.net"]
    base_url = 'http://bangla.samakal.net'
    content_body = {
        'css': 'div#newsDtl *::text'
    }
    start_request_url = base_url

    allowed_configurations = [
        ['start_date'],
        ['start_date', 'end_date'],
        ['category', 'start_date'],
        ['category', 'start_date', 'end_date'],
    ]

    rules = (
        Rule(
            LinkExtractor(
                # http://bangla.samakal.net/2016/06/01/215743
                allow=('/\d{4}/\d{2}/\d{2}/\d+$'),
                restrict_xpaths=('//div[@class="main-body"]')
            ),
            callback='parse_content'),
    )

    def request_index(self, response):
        categories = list(set(response.css('#topMenuItem a::attr("href")').re('/([^\/]+)/$')))

        if self.category is not None:
            if self.category in categories:
                categories = [self.category]
            else:
                raise ValueError('invalid category slug. available slugs: %s' % ", ".join(categories))

        date_processing = self.start_date
        while date_processing <= self.end_date:
            for category in categories:
                # redifining the rule again according to the specific date url
                SamakalSpider.rules = (Rule(LinkExtractor(allow=('/' + date_processing.strftime('%Y/%m/%d') + '/\d+$',),
                                                          restrict_xpaths=('//div[@class="main-body"]')),
                                            callback="parse_content", follow=True),)
                super(SamakalSpider, self)._compile_rules()
                # http://bangla.samakal.net/-education/2016/06/01 
                url = 'http://bangla.samakal.net/{0}/{1}'.format(
                    category,
                    date_processing.strftime('%Y/%m/%d')
                )
                yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)
