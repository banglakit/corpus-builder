# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry


# crawl page 1 to 5 of each category and subcategory
#
# scrapy crawl banglanews24 -a start_page=1
# scrapy crawl banglanews24 -a start_page=1 -a end_page=5
# scrapy crawl banglanews24 -a start_page=1 -a end_page=5 -a category=7
# scrapy crawl banglanews24 -a start_page=1 -a end_page=5 -a category=17 -a subcategory=5


class Banglanews24Spider(CrawlSpider):
    name = "banglanews24"
    allowed_domains = ["banglanews24.com"]

    rules = (
        Rule(
            LinkExtractor(
                # http://www.banglanews24.com/information-technology/news/497935/%E0%...
                allow=('\/[a-z-]*\/news\/\d+\/.*$')
            ),
            callback='parse_news'),
    )

    def __init__(self, start_page=None, end_page=None, category=None, subcategory=None, *a, **kw):

        if not (start_page or end_page):
            raise ValueError("start_page, end_page must be provided as arguments")

        self.start_page = int(start_page)
        if end_page:
            self.end_page = int(end_page)
        else:
            self.end_page = start_page

        self.category = None
        self.subcategory = None

        if category:
            self.category = int(category)
            if subcategory:
                self.subcategory = int(subcategory)
        elif subcategory:
            raise ValueError("subcategory must be accompanied by category")

        super(Banglanews24Spider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('http://www.banglanews24.com/',
                             callback=self.start_categorized_requests)

    def start_categorized_requests(self, response):
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

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = ("".join(response.css('#main-article p::text').extract())).strip()
        return item
