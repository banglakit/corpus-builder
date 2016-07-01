# -*- coding: utf-8 -*-
import datetime
import re
import urlparse

import dateutil.parser
import scrapy

from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


# different sets of categories are available on date-based and page-based crawling
#
# scrapy crawl ittefaq -a start_page=1
# scrapy crawl ittefaq -a start_page=1 -a end_page=5
# scrapy crawl ittefaq -a start_page=1 -a end_page=5 -a category=sports
# scrapy crawl ittefaq -a start_date='2016-06-05'
# scrapy crawl ittefaq -a start_date='2016-06-05' -a end_date='2016-06-05'
# scrapy crawl ittefaq -a start_date='2016-06-05' -a end_date='2016-06-05' -a category=sports-news

class IttefaqSpider(NewspaperSpider):
    name = "ittefaq"
    allowed_domains = ["ittefaq.com.bd"]
    base_url = 'http://www.ittefaq.com.bd'
    start_request_url = base_url

    news_body = {
        'css': 'div.details *::text'
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
                    url = self.base_url + '/{0}/{1}'.format(
                        category,
                        page_number
                    )
                    yield scrapy.Request(url, callback=self.start_news_requests)

        elif self.start_date:
            date_processing = self.start_date
            while date_processing <= self.end_date:
                for category in categories:
                    # http://www.ittefaq.com.bd/print-edition/sports-news/2016/06/30
                    url = self.base_url + '/print-edition/{0}/{1}'.format(
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