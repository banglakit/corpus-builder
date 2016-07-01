# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


# crawl page 1 to 5 of each category and subcategory
#
# scrapy crawl banglanews24 -a start_page=1
# scrapy crawl banglanews24 -a start_page=1 -a end_page=5
# scrapy crawl banglanews24 -a start_page=1 -a end_page=5 -a category=7
# scrapy crawl banglanews24 -a start_page=1 -a end_page=5 -a category=17 -a subcategory=5


class Banglanews24Spider(NewspaperSpider):
    name = "banglanews24"
    allowed_domains = ["banglanews24.com"]
    base_url = 'http://www.banglanews24.com'
    start_request_url = base_url
    news_body = {
        'css': '#main-article p::text'
    }

    allowed_configurations = [
        ['start_page'],
        ['start_page', 'end_page'],
        ['category', 'start_page'],
        ['category', 'start_page', 'end_page'],
    ]

    rules = (
        Rule(
            LinkExtractor(
                # http://www.banglanews24.com/information-technology/news/497935/%E0%...
                allow=('\/[a-z-]*\/news\/\d+\/.*$')
            ),
            callback='parse_news'),
    )

    def request_index(self, response):
        categories = []

        if not self.category:
            categories = list(set(response.css('.navbar-nav a::attr("href")').re('.*/category/.*') + \
                                  response.css('.navbar-nav a::attr("href")').re('.*/subcategory/.*')))
        else:
            if not self.subcategory:
                categories = response.css('.navbar-nav a::attr("href")').re('.*/category/.*/{0}/?$'.format(
                    self.category))
            else:
                categories = response.css('.navbar-nav a::attr("href")').re('*/subcategory/.*/{0}/{1}/?$'.format(
                    self.category, self.subcategory))
            if not categories:
                raise ValueError('invalid category or subcategory id')

        for category_url in categories:
            for page_number in range(self.start_page, self.end_page + 1):
                yield scrapy.Request(category_url + '?page={0}'.format(page_number),
                                     callback=self.start_news_requests)

    def start_news_requests(self, response):
        news_links = list(set(response.css('a::attr("href")').re(".*\/news\/.*")))

        for link in news_links:
            yield self.make_requests_from_url(link)
