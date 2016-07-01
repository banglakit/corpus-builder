# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 20:56:43 2016

@author: hasnayeen
"""

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry


class AmaderSomoySpider(CrawlSpider):
    name = 'amader_somoy'
    allowed_domains = ['dainikamadershomoy.com']
    start_urls = ['http://www.dainikamadershomoy.com/all-news/']

    rules = (
        Rule(LinkExtractor(
            allow='(?<=com)\/\w.*\/\d.*\/.*'
        ),
        callback='parse_news'),
    )
    
    def init(self, start_page=None, end_page=None, category=None, *a, **kw):
        
        if not (start_page or end_page):
            raise ValueError('Start page, end page must be provided as arguments')
            
        self.start_page = int(start_page)
        if end_page:
            self.end_page = int(end_page)
        else:
            self.end_page = int(self.start_page)
            
        self.category = None
        
        if category:
            self.category = category
            
        super(AmaderSomoySpider, self).__init__(*a, **kw)
        
    def start_requests(self):
        yield scrapy.Request('http://www.dainikamadershomoy.com/',
                             callback = self.start_categorized_requests)
                             
    def start_categorized_requests(self, response):
        categories = []
        if not self.category:
            categories = list(set(response.css('#menu_category a::attr("href")')))
        else:
            categories = response.css('#menu_category a::attr("href")').re('{0}'.format(self.category))

        if not categories:
            raise ValueError('Invalid category')
            
        for category in categories:
            for page in range(int(self.start_page), int(self.end_page) + 1):
                yield scrapy.Request('http://dainikamadershomoy.com/all-news/' + category + '/?pg={0}'.format(str(page)),
                                     callback=self.start_news_requests)

    def start_news_requests(self, response):
        news_links = list(set(response.css('.all_news_content_block a::attr("href")').extract()))

        for link in news_links:
            yield self.make_requests_from_url(link)
                    
    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(part for part in response.css('.dtl_section p::text').extract())
        return item
