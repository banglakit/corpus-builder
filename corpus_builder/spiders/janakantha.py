# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry

class JanokanthaSpider(CrawlSpider):
    name = "janokantha"
    allowed_domains = ["dailyjanakantha.com"]

    rules = (
    	Rule(
    		LinkExtractor(
                        # https://www.dailyjanakantha.com/details/article/194671/%E0%A6%AA%E0%A6%A5%E0%A7%87-%E0%A6%AA%E0%A6%A5%E0%A7%87-%E0%A6%9A%E0%A6%BE%E0%A6%81%E0%A6%A6%E0%A6%BE%E0%A6%AC%E0%A6%BE%E0%A6%9C%E0%A6%BF
    			allow=('/details/article/\d+/[^\/]+$'),
                        restrict_xpaths=('//div[@class="content"]')  
    		),
    		callback='parse_news'),
    )
    
    def __init__(self, start_date=None, end_date=None, *a, **kw):
    	self.start_date = dateutil.parser.parse(start_date)
    	self.end_date = dateutil.parser.parse(end_date)

        self.categories = ['frontpage', 'lastpage', 'others', 'national', 
        'sports', 'editorial', 'quadruple', 'international', 'trade', 
        'finance', 'education', 'reopinion', 'cities']

    	super(JanokanthaSpider, self).__init__(*a, **kw)

    def start_requests(self):
    	date_processing = self.start_date
    	while date_processing <= self.end_date:
            for category in self.categories:
                # https://www.dailyjanakantha.com/frontpage/date/2016-06-01
        		url = 'http://www.dailyjanakantha.com/{0}/date/{1}'.format(
                    category,
        			date_processing.strftime('%Y-%m-%d')
        		)
        		yield self.make_requests_from_url(url)
            date_processing += datetime.timedelta(days=1)

    def parse_news(self, response):
    	item = TextEntry()
    	item['body'] = "".join(part for part in response.css('p.artDetails *::text').extract())
    	return item
        
