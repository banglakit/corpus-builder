# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry

# different sets of categories are available on date-based and page-based crawling
#
# scrapy crawl bangladesh_pratidin -a start_page=1
# scrapy crawl bangladesh_pratidin -a start_page=1 -a end_page=5
# scrapy crawl bangladesh_pratidin -a start_page=1 -a end_page=5 -a category=special
# scrapy crawl bangladesh_pratidin -a start_date='2016-06-05'
# scrapy crawl bangladesh_pratidin -a start_date='2016-06-05' -a end_date='2016-06-05'
# scrapy crawl bangladesh_pratidin -a start_date='2016-06-05' -a end_date='2016-06-05' -a category=first-page


class BangladeshPratidinSpider(scrapy.Spider):
    name = "bangladesh_pratidin"
    allowed_domains = ["bd-pratidin.com"]
    
    def __init__(self, start_date=None, end_date=None, start_page=None, end_page=None,
        category=None, *a, **kw):

        if (start_date or end_date) and (start_page or end_page):
            raise AttributeError("date-based and paginated crawling cannot be used together")

        if not ((start_date or end_date) or (start_page or end_page)):
            raise ValueError("either dates or page numbers must be provided")

        if start_page is not None:
            self.start_page = int(start_page)
        else:
            self.start_page = None

        if end_page is not None:
            self.end_page = int(end_page)
        elif start_page is not None:
            self.end_page = self.start_page
        else:
            self.end_page = None

        if start_date is not None:
            self.start_date = dateutil.parser.parse(start_date)
        else:
            self.start_date = None

        if end_date is not None:
            self.end_date = dateutil.parser.parse(end_date)
        elif start_date is not None:
            self.end_date = self.start_date
        else:
            self.end_date = None

        if category is not None:
            self.category = category
        else:
            self.category = None

        super(BangladeshPratidinSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('http://www.bd-pratidin.com/',
            callback=self.start_categorized_requests)

    def start_categorized_requests(self, response):
        categories = []
        if self.start_page:
            categories = response.css('ul.nav a::attr(href)').re('^(?!http:).*$')
            unwanted_categories = response.css('ul.nav .dropdown-menu a::attr(href)').re('^(?!http:).*$')
            categories = [x for x in list(set(categories) - set(unwanted_categories)) \
                if (not x == "" and not x == "#")]
        elif self.start_date:
            categories = list(set(response.css('ul.nav .dropdown-menu a::attr(href)').re('^(?!http:).*$')))
            categories = [x for x in categories if (not x == "" and not x == "#")]

        if self.category:
            if self.category in categories:
                categories = [self.category]
            else:
                raise ValueError('invalid category slug. available slugs: %s' % str(categories))

        if self.start_page:
            for category in categories:
                for page_number in range(self.start_page, self.end_page+1):
                    # http://www.bd-pratidin.com/special/6  
                    if page_number <= 1:
                        pgn = 0
                    else:
                        pgn = page_number*6
                    url = 'http://www.bd-pratidin.com/{0}/{1}'.format(
                        category,
                        pgn
                    )
                    yield scrapy.Request(url, callback=self.start_news_requests)

        elif self.start_date:
            date_processing = self.start_date
            while date_processing <= self.end_date:
                for category in categories:
                    # http://www.bd-pratidin.com/first-page/2016/06/01
                    url = 'http://www.bd-pratidin.com/{0}/{1}'.format(
                        category,
                        date_processing.strftime('%Y/%m/%d')
                    )
                    yield scrapy.Request(url, callback=self.start_news_requests)
                date_processing += datetime.timedelta(days=1)
        else:
            raise ValueError("either dates or page numbers must be provided")

    def start_news_requests(self, response):
        news_links = list(set(response.xpath('.//h1/parent::a/@href').extract()))

        for link in news_links:
            if link[:4] != 'http':
                link = 'http://www.bd-pratidin.com/' + link
            yield scrapy.Request(link, callback=self.parse_news)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = ("".join(response.css('#newsDtl p::text').extract())).strip()
        return item
