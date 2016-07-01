# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


class InqilabSpider(NewspaperSpider):
    name = "inqilab"
    allowed_domains = ["dailyinqilab.com"]
    base_url = 'http://www.dailyinqilab.com'
    start_request_url = base_url

    news_body = {
        'css': 'div.post-article p *::text'
    }

    allowed_configurations = [
        ['archive', 'start_date'],
        ['archive', 'start_date', 'end_date']
    ]

    rules = (
        Rule(
            LinkExtractor(
                # https://www.dailyinqilab.com/details/21415/%E0%A6%95%E0%A7%87%E0%A6%B0%E0%A6%BE%E0%A6%A8%E0%A7%80%E0%A6%97%E0%A6%9E%E0%A7%8D%E0%A6%9C%E0%A7%87-%E0%A7%A9-%E0%A6%B6%E0%A7%8D%E0%A6%B0%E0%A6%AE%E0%A6%BF%E0%A6%95-%E0%A6%A6%E0%A6%97%E0%A7%8D%E0%A6%A7
                allow=('/details/\d+/[^\/]+$'),
                restrict_xpaths=('//div[@class="mag-cat-post"]')
            ),
            callback='parse_news'),
    )

    def request_index(self, response):
        date_processing = self.start_date
        while date_processing <= self.end_date:
            # https://www.dailyinqilab.com/archive_index.php?option=1&publish_date=2016-06-01
            url = self.base_url + '/archive_index.php?option=1&publish_date={0}'.format(
                date_processing.strftime('%Y-%m-%d')
            )
            yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)
