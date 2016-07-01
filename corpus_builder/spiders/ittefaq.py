# -*- coding: utf-8 -*-
import datetime
import re
import urlparse

import dateutil.parser
import scrapy

from corpus_builder.items import TextEntry


# different sets of categories are available on date-based and page-based crawling
#
# scrapy crawl ittefaq -a start_page=1
# scrapy crawl ittefaq -a start_page=1 -a end_page=5
# scrapy crawl ittefaq -a start_page=1 -a end_page=5 -a category=sports
# scrapy crawl ittefaq -a start_date='2016-06-05'
# scrapy crawl ittefaq -a start_date='2016-06-05' -a end_date='2016-06-05'
# scrapy crawl ittefaq -a start_date='2016-06-05' -a end_date='2016-06-05' -a category=sports-news

class IttefaqSpider(scrapy.Spider):
    name = "ittefaq"
    allowed_domains = ["ittefaq.com.bd"]

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

        self.category = category

        super(IttefaqSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('http://www.ittefaq.com.bd/',
                             callback=self.start_categorized_requests)

    def start_categorized_requests(self, response):
        if self.start_page:
            all_categories = response.css('#menu a::attr("href")').extract()
            print_categories = response.css('#menu a::attr("href")').re('.*print-edition.*')
            categories = [urlparse.urlparse(x.strip()).path.split('/')[-1] \
                          for x in list(set(all_categories) - set(print_categories))]
        elif self.start_date:
            categories = list(set(response.css('#menu a::attr("href")').re('.*/print-edition/.*')))
            categories = [re.match('.*\/(.*)\/\d{4}\/\d{2}\/\d{2}', x).groups()[0] for x in categories \
                          if (not x == "" and not x == "#")]

        if self.category:
            if self.category in categories:
                categories = [self.category]
            else:
                raise ValueError('invalid category slug. available slugs: %s' % str(categories))

        if self.start_page:
            for category in categories:
                for page_number in range(self.start_page, self.end_page + 1):
                    # http://www.ittefaq.com.bd/sports/10
                    url = 'http://www.ittefaq.com.bd/{0}/{1}'.format(
                        category,
                        page_number
                    )
                    yield scrapy.Request(url, callback=self.start_news_requests)

        elif self.start_date:
            date_processing = self.start_date
            while date_processing <= self.end_date:
                for category in categories:
                    # http://www.ittefaq.com.bd/print-edition/sports-news/2016/06/30
                    url = 'http://www.ittefaq.com.bd/print-edition/{0}/{1}'.format(
                        category,
                        date_processing.strftime('%Y/%m/%d')
                    )
                    yield scrapy.Request(url, callback=self.start_news_requests)
                date_processing += datetime.timedelta(days=1)
        else:
            raise ValueError("either dates or page numbers must be provided")

    def start_news_requests(self, response):
        news_links = list(set(response.css('div.headline a::attr("href")').extract()))

        for link in news_links:
            yield scrapy.Request(link, callback=self.parse_news)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(response.css('div.details span::text').extract())
        return item
