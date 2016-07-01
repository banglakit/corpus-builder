# -*- coding: utf-8 -*-
import datetime
import urlparse

import dateutil.parser
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


class JanakanthaSpider(NewspaperSpider):
    name = "janakantha"
    allowed_domains = ["dailyjanakantha.com"]
    base_url = 'https://www.dailyjanakantha.com'
    start_request_url = base_url

    news_body = {
        'css': 'p.artDetails *::text'
    }

    allowed_configurations = [
        ['start_date'],
        ['start_date', 'end_date'],
        ['category', 'start_date'],
        ['category', 'start_date', 'end_date'],
    ]

    def request_index(self, response):
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
                url = self.base_url + '/{0}/date/{1}'.format(
                    category,
                    date_processing.strftime('%Y-%m-%d')
                )
                yield scrapy.Request(url, callback=self.extract_news_category)
            date_processing += datetime.timedelta(days=1)

    def extract_news_category(self, response):
        news_links = list(set(response.xpath('//div[@class="content"]//a').extract()))

        for link in news_links:
            if not link[:4] == 'http':
                link = self.base_url + link
            yield scrapy.Request(link, callback=self.parse_news)
