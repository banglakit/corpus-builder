# -*- coding: utf-8 -*-
import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from corpus_builder.templates.spider import CommonSpider


class BanglatribuneSpider(CommonSpider):
    name = "banglatribune"
    allowed_domains = ["www.banglatribune.com"]
    start_urls = (
        'http://www.banglatribune.com/archive/',
    )
    base_url = 'http://www.banglatribune.com/archive'
    start_request_url = base_url

    news_body = {
        'xpath': '//div[@itemprop="articleBody"]/p/text()'
    }

    allowed_configurations = [
        ['start_date', 'end_date']
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow='\/[a-z-]*\/news\/\d{6}\/.*$',
                restrict_css='.summery_view'
            ),
            callback='parse_news'
        ),
        Rule(
            LinkExtractor(
                allow='\/\d{4}-\d{2}-\d{2}\?page=\d+'
            ),
            callback='extract_links'
        ),
    )

    def request_index(self, response):
        if self.start_date:
            date_processing = self.start_date
            while date_processing <= self.end_date:
                url = self.base_url + '/{0}?page=1'.format(date_processing.strftime('%Y-%m-%d'))
                yield self.make_requests_from_url(url)
                date_processing += datetime.timedelta(days=1)

    def extract_links(self, response):
        news_links = list(
            set(response.xpath('//h2[@class="title_holder"]/a/@href').re('(?!http:)[a-z-]*\/news\/\d{6}\/.*$')))
        for link in news_links:
            if link[:4] != 'http':
                link = 'http://www.banglatribune.com/' + link
            yield self.make_requests_from_url(link)
