# -*- coding: utf-8 -*-
import scrapy
import datetime

import dateutil.parser
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry
from corpus_builder.templates.spider import NewspaperSpider


class ProthomAloSpider(NewspaperSpider):
    name = "prothom_alo"
    allowed_domains = ["prothom-alo.com"]
    base_url = "http://www.prothom-alo.com"
    allowed_configurations = [
        ['start_page', 'end_page'],
        ['start_page'],
        ['archive', 'start_date'],
        ['archive', 'start_date', 'end_date'],
        ['category', 'start_page'],
        ['category', 'start_page', 'end_page']
    ]

    start_request_url = base_url

    news_body = {
        'xpath': '//article//text()'
    }

    def request_index(self, response):
        if not self.archive:
            categories = response.xpath('.//ul[@id=1]/li/a/@href').re('^[a-z0-9-]*$')
            categories.remove('todays-paper')

            # implement someday
            # subcategories = response.xpath('.//ul[@id=1]/li/a[@href="{0}"]/../ul/li/a/@href').re('^[a-z0-9-]*$'.format(
            #             category)

            if self.category:
                if self.category in categories:
                    categories = [self.category]
                else:
                    raise ValueError('invalid category slug. available slugs: \'%s\'' % "', '".join(categories))

            if self.start_page:
                for category in categories:
                    # http://www.prothom-alo.com/opinion/article?page=2
                    for page_number in range(self.start_page, self.end_page + 1):
                        url = self.base_url + '/{0}/article?page={1}'.format(category, page_number)
                        yield scrapy.Request(url, callback=self.extract_news_category)
        else:
            date_processing = self.start_date
            while date_processing <= self.end_date:
                url = self.base_url + '/archive/{0}'.format(date_processing.strftime('%Y-%m-%d'))
                yield scrapy.Request(url, callback=self.extract_news_archive)
        
                date_processing += datetime.timedelta(days=1)

    def extract_news_category(self, response):
        news_links = list(set(response.css('.blog_archive_widget a::attr("href")').extract()))

        for link in news_links:
            if not link[:4] == 'http':
                link = self.base_url + link
            yield scrapy.Request(link, callback=self.parse_news)

    def extract_news_archive(self, response):
        news_links = list(set(response.css('.all_titles_widget a::attr("href")').extract()))

        for link in news_links:
            if not link[:4] == 'http':
                link = self.base_url + link
            yield scrapy.Request(link, callback=self.parse_news)