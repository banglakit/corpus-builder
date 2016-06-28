# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry

# Note: The spider only works for the "Printed Edition", for now.


class BangladeshPratidinSpider(CrawlSpider):
    name = "bangladesh_pratidin"
    allowed_domains = ["bd-pratidin.com"]

    rules = (
    	Rule(
    		LinkExtractor(
                # http://www.bd-pratidin.com/first-page/2016/06/01/148170
    			allow=('\/\d{4}\/\d{2}\/\d{2}\/\d+$')
    		),
    		callback='parse_news'),
    )
    
    def __init__(self, start_date=None, end_date=None, *a, **kw):
    	self.start_date = dateutil.parser.parse(start_date)
    	self.end_date = dateutil.parser.parse(end_date)

        self.categories = ['first-page', 'entertainment-news', 'last-page', 'news',
        'city', 'country-village', 'sport-news', 'various', 'international', 'editorial']

    	super(BangladeshPratidinSpider, self).__init__(*a, **kw)

    def start_requests(self):
    	date_processing = self.start_date
    	while date_processing <= self.end_date:
            for category in self.categories:
                # http://www.bd-pratidin.com/first-page/2016/06/01
        		url = 'http://www.bd-pratidin.com/{0}/{1}'.format(
                    category,
        			date_processing.strftime('%Y/%m/%d')
        		)
        		yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
    	item = TextEntry()
    	item['body'] = "".join(part for part in response.css('#newsDtl p::text').extract())
    	return item
