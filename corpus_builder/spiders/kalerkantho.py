# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry

# Note: The spider only works for the "Printed Edition", for now.


class KalerkanthoSpider(CrawlSpider):
    name = "kalerkantho"
    allowed_domains = ["kalerkantho.com"]

    rules = (
    	Rule(
    		LinkExtractor(
                        # http://www.kalerkantho.com/print-edition/first-page/2016/06/16/370418
    			allow=('\/\d{4}\/\d{2}\/\d{2}\/\d+$'),
                        restrict_css=('div.print_edition_left')
    		),
    		callback='parse_news'),
    )
    
    def __init__(self, start_date=None, end_date=None, *a, **kw):
    	self.start_date = dateutil.parser.parse(start_date)
    	self.end_date = dateutil.parser.parse(end_date)

        self.categories = []

    	super(KalerkanthoSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('http://www.kalerkantho.com/print-edition/',
                             callback = self.start_categorized_requests)

    def start_categorized_requests(self, response):
        self.categories = list(set(response.css('.nav.navbar-nav li a::attr("href")').re('/print\-edition\/([^\/]+)$')))

        if not self.categories:
            raise ValueError('No categories found')

    	date_processing = self.start_date
    	while date_processing <= self.end_date:
            for category in self.categories:
                # http://www.kalerkantho.com/print-edition/country/2016/06/29
        		url = 'http://www.kalerkantho.com/print-edition/{0}/{1}'.format(
                    category,
        			date_processing.strftime('%Y/%m/%d')
        		)
        		yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
    	item = TextEntry()
    	item['body'] = "".join(part for part in response.css('div.details p *::text').extract())
    	return item
        
