# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry

# Note: The spider only works for the "Printed Edition", for now.
# Note: This spider works only on Page #1, pagination is under development


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
    
    def __init__(self, start_date=None, end_date=None, start_page=None, end_page=None,
        category=None, subcategory=None, *a, **kw):

        if start_date or end_date:
            raise NotImplementedError("date-based crawling has not been implemented for this crawler.")

        if not (start_page or end_page):
            raise ValueError("start_page, end_page must be provided as arguments")

        self.start_page = start_page
        self.end_page = end_page
        if category:
            self.category = int(category)
        else:
            self.category = None
        if subcategory:
            self.subcategory = int(subcategory)

    	super(Banglanews24Spider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('http://www.banglanews24.com/',
            callback=self.start_categorized_requests)

    def start_categorized_requests(self, response):
        if not self.category:
            categories = list(set(response.css('.navbar-nav a::attr("href")').re('.*/category/.*') + \
                response.css('.navbar-nav a::attr("href")').re('.*/subcategory/.*')))

            for category_url in categories:
            	yield scrapy.Request(category_url, callback=self.start_news_requests)
        else:
            raise NotImplementedError("category-based crawling not implemented yet")

    def start_news_requests(self, response):
        news_links = list(set(response.css('a::attr("href")').re(".*\/news\/.*")))

        for link in news_links:
            yield self.make_requests_from_url(link)

    def parse_news(self, response):
    	item = TextEntry()
    	item['body'] = ("".join(response.css('#main-article p::text').extract())).strip()
    	return item
