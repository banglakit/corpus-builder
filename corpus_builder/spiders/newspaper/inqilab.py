# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry


class InqilabSpider(CrawlSpider):
    name = "inqilab"
    allowed_domains = ["dailyinqilab.com"]

    rules = (
        Rule(
            LinkExtractor(
                # https://www.dailyinqilab.com/details/21415/%E0%A6%95%E0%A7%87%E0%A6%B0%E0%A6%BE%E0%A6%A8%E0%A7%80%E0%A6%97%E0%A6%9E%E0%A7%8D%E0%A6%9C%E0%A7%87-%E0%A7%A9-%E0%A6%B6%E0%A7%8D%E0%A6%B0%E0%A6%AE%E0%A6%BF%E0%A6%95-%E0%A6%A6%E0%A6%97%E0%A7%8D%E0%A6%A7
                allow=('/details/\d+/[^\/]+$'),
                restrict_xpaths=('//div[@class="mag-cat-post"]')
            ),
            callback='parse_news'),
    )

    def __init__(self, start_date=None, end_date=None, *a, **kw):
        self.start_date = dateutil.parser.parse(start_date)
        self.end_date = dateutil.parser.parse(end_date)

        # no category,all links dumped in a page -_-

        super(InqilabSpider, self).__init__(*a, **kw)

    def start_requests(self):
        date_processing = self.start_date
        while date_processing <= self.end_date:
            # https://www.dailyinqilab.com/archive_index.php?option=1&publish_date=2016-06-01
            url = 'http://www.dailyinqilab.com/archive_index.php?option=1&publish_date={0}'.format(
                date_processing.strftime('%Y-%m-%d')
            )
            yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(part for part in response.css('div.post-article p *::text').extract())
        return item
