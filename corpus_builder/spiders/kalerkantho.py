# -*- coding: utf-8 -*-
import datetime

import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry


# Note: The spider only works for the "Printed Edition", for now.


class KalerkanthoSpider(CrawlSpider):
    name = "kalerkantho"
    allowed_domains = ["kalerkantho.com"]

    rules = (
        Rule(
            LinkExtractor(
                # http://www.kalerkantho.com/print-edition/first-page/2016/06/16/370418
                allow=('\/\d{4}\/\d{2}\/\d{2}\/\d+$')
            ),
            callback='parse_news'),
    )

    def __init__(self, start_date=None, end_date=None, *a, **kw):
        self.start_date = dateutil.parser.parse(start_date)
        self.end_date = dateutil.parser.parse(end_date)

        self.categories = ['first-page', 'last-page', 'sports', 'industry-business',
                           'deshe-deshe', 'priyo-desh', 'tech-everyday', 'education',
                           'editorial', 'sub-editorial', 'drishtikon', 'muktadhara', 'letters']

        super(KalerkanthoSpider, self).__init__(*a, **kw)

    def start_requests(self):
        date_processing = self.start_date
        while date_processing <= self.end_date:
            for category in self.categories:
                # http://www.kalerkantho.com/print-edition/country/2016/06/29
                url = 'http://www.kalerkantho.com/print-edition/{0}/{1}'.format(
                    category,
                    date_processing.strftime('%Y/%m/%d')
                )
                yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(part for part in response.css('div.details p *::text').extract())
        return item
