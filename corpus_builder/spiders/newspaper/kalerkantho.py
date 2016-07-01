# -*- coding: utf-8 -*-
import datetime
import urlparse
import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


# Note: The spider only works for the "Printed Edition", for now.


class KalerkanthoSpider(NewspaperSpider):
    name = "kalerkantho"
    allowed_domains = ["kalerkantho.com"]
    base_url = 'http://www.kalerkantho.com'
    start_request_url = base_url
    news_body = {
        'css': 'div.details p *::text'
    }

    rules = (
        Rule(
            LinkExtractor(
                # http://www.kalerkantho.com/print-edition/first-page/2016/06/16/370418
                allow=('\/\d{4}\/\d{2}\/\d{2}\/\d+$')
            ),
            callback='parse_news'),
    )

    allowed_configurations = [
        ['start_date'],
        ['start_date', 'end_date'],
        ['category', 'start_date'],
        ['category', 'start_date', 'end_date'],
    ]

    def request_index(self, response):
        print_categories = response.css('.taday_newspaper li.col-sm-2 a::attr("href")').extract()
        print_categories = [urlparse.urlparse(x).path.split('/')[-1] for x in print_categories]

        # hack
        categories = print_categories

        if self.category:
            if self.category in categories:
                categories = [self.category]
            else:
                raise ValueError('invalid category slug. available slugs: %s' % ", ".join(categories))

        date_processing = self.start_date
        while date_processing <= self.end_date:
            for category in categories:
                # http://www.kalerkantho.com/print-edition/country/2016/06/29
                url = self.base_url + '/print-edition/{0}/{1}'.format(
                    category,
                    date_processing.strftime('%Y/%m/%d')
                )
                yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)
