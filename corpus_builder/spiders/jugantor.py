# -*- coding: utf-8 -*-
import datetime

import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry


class JugantorSpider(CrawlSpider):
    name = "jugantor"
    allowed_domains = ["jugantor.com"]

    rules = (
        Rule(
            LinkExtractor(
                # http://www.jugantor.com/first-page/2016/06/28/42001/%E0%A6%B8%E0%A6%AC%E0%A6%87-%E0%A6%9C%E0%A6%BE%E0%A6%A8%E0%A7%87-%E0%A6%AA%E0%A7%81%E0%A6%B2%E0%A6%BF%E0%A6%B6
                allow=('\/\d{4}\/\d{2}\/\d{2}\/\d+/[^\/]+$'),
                restrict_xpaths=('//div[@class="home_page_left"]')
            ),
            callback='parse_news'),
    )

    def __init__(self, start_date=None, end_date=None, *a, **kw):
        self.start_date = dateutil.parser.parse(start_date)
        self.end_date = dateutil.parser.parse(end_date)

        self.categories = ['first-page', 'last-page', 'sports', 'news', 'ten-horizon',
                           'industry-trade', 'anando-nagar', 'oneday-everyday', 'tutorial', 'window', 'sub-editorial',
                           'bangla-face', 'city', 'it-world', 'out-of-home', 'editorial', 'country-news']

        super(JugantorSpider, self).__init__(*a, **kw)

    def start_requests(self):
        date_processing = self.start_date
        while date_processing <= self.end_date:
            for category in self.categories:
                # http://www.jugantor.com/news/2016-06-28
                url = 'http://www.jugantor.com/{0}/{1}'.format(
                    category,
                    date_processing.strftime('%Y/%m/%d')
                )
                yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(part for part in response.css('div#myText *::text').extract())
        return item
