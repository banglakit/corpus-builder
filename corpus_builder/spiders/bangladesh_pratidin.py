# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider

# different sets of categories are available on date-based and page-based crawling
#
# scrapy crawl bangladesh_pratidin -a start_page=1
# scrapy crawl bangladesh_pratidin -a start_page=1 -a end_page=5
# scrapy crawl bangladesh_pratidin -a start_page=1 -a end_page=5 -a category=special
# scrapy crawl bangladesh_pratidin -a start_date='2016-06-05'
# scrapy crawl bangladesh_pratidin -a start_date='2016-06-05' -a end_date='2016-06-05'
# scrapy crawl bangladesh_pratidin -a start_date='2016-06-05' -a end_date='2016-06-05' -a category=first-page


class BangladeshPratidinSpider(NewspaperSpider):
    name = "bangladesh_pratidin"
    allowed_domains = ["bd-pratidin.com"]
    base_url = 'http://www.bd-pratidin.com'
    start_request_url = base_url

    news_body = {
        'css': '#newsDtl p::text'
    }

    allowed_configurations = [
        ['start_page', 'end_page'],
        ['start_page'],
        ['category', 'start_page'],
        ['category', 'start_page', 'end_page'],
        ['start_date', 'end_date'],
        ['start_date'],
        ['category', 'start_date'],
        ['category', 'start_date', 'end_date']
    ]  

    def request_index(self, response):
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
                raise ValueError('invalid category slug. available slugs: %s' % ", ".join(categories))

        if self.start_page:
            for category in categories:
                for page_number in range(self.start_page, self.end_page+1):
                    # http://www.bd-pratidin.com/special/6  
                    if page_number <= 1:
                        pgn = 0
                    else:
                        pgn = page_number*6
                    url = self.base_url + '/{0}/{1}'.format(
                        category,
                        pgn
                    )
                    yield scrapy.Request(url, callback=self.start_news_requests)

        elif self.start_date:
            date_processing = self.start_date
            while date_processing <= self.end_date:
                for category in categories:
                    # http://www.bd-pratidin.com/first-page/2016/06/01
                    url = self.base_url + '/{0}/{1}'.format(
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
                link = self.base_url + '/' + link
            yield scrapy.Request(link, callback=self.parse_news)

