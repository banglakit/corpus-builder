# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


class BhorerkagojSpider(NewspaperSpider):
    name = 'bhorerkagoj'
    allowed_domains = ['bhorerkagoj.net']
    base_url = 'http://www.bhorerkagoj.net' + '/online'
    start_request_url = base_url

    news_body = {
        'css': 'div.entry p::text'
    }

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page'],
        ['category', 'start_page'],
        ['category', 'start_page', 'end_page']
    ]

    rules = (
        Rule(LinkExtractor(
            allow='\/\d{4}\/\d{2}\/\d{2}\/\d+\.php$'
        ),
            callback='parse_news'),
    )

    def request_index(self, response):
        categories = []
        if not self.category:
            categories = list(set(response.css('#navcatlist a::attr("href")').re('(?<=category/).*')))
        else:
            categories = response.css('#navcatlist a::attr("href")').re('category/{0}'.format(self.category))
            if not categories:
                categories = list(set(response.css('#navcatlist a::attr("href")').re('(?<=category/).*')))
                raise ValueError('invalid category slug. available slugs: \'%s\'' % "', '".join(categories))

        for category in categories:
            for page in range(self.start_page, self.end_page + 1):
                yield scrapy.Request(self.base_url + '/category/' + category + '/page/{0}'.format(str(page)),
                                     callback=self.start_news_requests)

    def start_news_requests(self, response):
        news_links = list(set(response.css('.news-box h3 a::attr("href")').extract()))

        for link in news_links:
            yield self.make_requests_from_url(link)

