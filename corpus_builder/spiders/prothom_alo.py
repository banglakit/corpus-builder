# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry


class ProthomAloSpider(CrawlSpider):
    name = "prothom_alo"
    allowed_domains = ["prothom-alo.com"]

    rules = (
    	Rule(
    		LinkExtractor(
    			allow=('\/article\/')
    		),
    		callback='parse_news'),
    )
    
    def __init__(self, start_date=None, end_date=None, *a, **kw):
    	self.start_date = dateutil.parser.parse(start_date)
    	self.end_date = dateutil.parser.parse(end_date)
    	super(ProthomAloSpider, self).__init__(*a, **kw)

    def start_requests(self):
    	date_processing = self.start_date
    	while date_processing <= self.end_date:
    		url = 'http://www.prothom-alo.com/archive/{0}'.format(
    			date_processing.strftime('%Y-%m-%d')
    		)
    		yield self.make_requests_from_url(url)

    		date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
    	item = TextEntry()
    	article_text_children = response.xpath('//article//text()').extract()
    	item['body'] = "".join(child for child in article_text_children)
    	return item
        
