# -*- coding: utf-8 -*-
import datetime
import urlparse

import dateutil.parser
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry


class JanakanthaSpider(CrawlSpider):
    name = "janakantha"
    allowed_domains = ["dailyjanakantha.com"]

    rules = (
        Rule(
            LinkExtractor(
                # https://www.dailyjanakantha.com/details/article/194671/%E0%A6%AA%E0%A6%A5%E0%A7%87-%E0%A6%AA%E0%A6%A5%E0%A7%87-%E0%A6%9A%E0%A6%BE%E0%A6%81%E0%A6%A6%E0%A6%BE%E0%A6%AC%E0%A6%BE%E0%A6%9C%E0%A6%BF
                allow=('/details/article/\d+/[^\/]+$'),
                restrict_xpaths=('//div[@class="content"]')
            ),
            callback='parse_news'),
    )

    def __init__(self, start_date=None, end_date=None, category=None, *a, **kw):
        self.start_date = dateutil.parser.parse(start_date)

        if end_date:
            self.end_date = dateutil.parser.parse(end_date)
        else:
            self.end_date = self.start_date

        self.category = category or None

        super(JanakanthaSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('https://www.dailyjanakantha.com/',
                             callback=self.start_categorized_requests)

    def start_categorized_requests(self, response):
        menu_links = [urlparse.urlparse(x.strip()).path.split('/')[-1] \
                      for x in response.css('nav.menu a::attr("href")').extract()]
        categories = [x for x in menu_links if (not x == "" and not x == "#")]

        if self.category is not None:
            if self.category in categories:
                categories = [self.category]
            else:
                raise ValueError('invalid category slug. available slugs: %s' % ", ".join(categories))

        date_processing = self.start_date
        while date_processing <= self.end_date:
            for category in categories:
                # https://www.dailyjanakantha.com/frontpage/date/2016-06-01
                url = 'https://www.dailyjanakantha.com/{0}/date/{1}'.format(
                    category,
                    date_processing.strftime('%Y-%m-%d')
                )
                yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(part for part in response.css('p.artDetails *::text').extract())
        return item
