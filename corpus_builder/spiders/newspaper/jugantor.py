# -*- coding: utf-8 -*-
import datetime
import urlparse
import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


class JugantorSpider(NewspaperSpider):
    name = "jugantor"
    allowed_domains = ["jugantor.com"]
    base_url = 'http://www.jugantor.com'
    start_request_url = base_url
    news_body = {
        'css': 'div#myText *::text'
    }

    allowed_configurations = [
        ['start_date'],
        ['start_date', 'end_date'],
        ['category', 'start_date'],
        ['category', 'start_date', 'end_date']
    ]

    rules = (
        Rule(
            LinkExtractor(
                # http://www.jugantor.com/first-page/2016/06/28/42001/%E0%A6%B8%E0%A6...
                allow=('\/\d{4}\/\d{2}\/\d{2}\/\d+/[^\/]+$'),
                restrict_xpaths=('//div[@class="home_page_left"]')
            ),
            callback='parse_news'),
    )

    def request_index(self, response):
        # online_categories = list(set(response.xpath('.//div[@id="menu_category"]/ul/li/a/@href').extract()))
        categories = list(set(response.xpath('.//div[@id="menu_category"]/ul/li/ul/li/a/@href').extract()))
        categories = [urlparse.urlparse(x).path.split('/')[-1] for x in categories]

        if self.category is not None:
            if self.category in categories:
                categories = [self.category]
            else:
                raise ValueError('invalid category slug. available slugs: %s' % ", ".join(categories))

        date_processing = self.start_date
        while date_processing <= self.end_date:
            for category in categories:
                # http://www.jugantor.com/news/2016-06-28
                url = self.base_url + '/{0}/{1}'.format(
                    category,
                    date_processing.strftime('%Y/%m/%d')
                )
                yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)