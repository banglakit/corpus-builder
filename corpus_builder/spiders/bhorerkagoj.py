# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from corpus_builder.items import TextEntry


class BhorerkagojSpider(CrawlSpider):
    name = 'bhorerkagoj'
    allowed_domains = ['bhorerkagoj.net']
    start_urls = ['http://www.bhorerkagoj.net/online/']

    rules = (
        Rule(LinkExtractor(
            allow='\/\d{4}\/\d{2}\/\d{2}\/\d+\.php$'
        ),
            callback='parse_news'),
    )

    def __init__(self, start_page=None, end_page=None, category=None, *a, **kw):

        if not (start_page or end_page):
            raise ValueError("start_page, end_page must be provided as arguments")

        self.start_page = int(start_page)
        if end_page:
            self.end_page = int(end_page)
        else:
            self.end_page = self.start_page

        self.category = category

        super(BhorerkagojSpider, self).__init__(*a, **kw)

    def start_requests(self):
        yield scrapy.Request('http://bhorerkagoj.net/online',
                             callback=self.start_categorized_requests)

    def start_categorized_requests(self, response):
        categories = []
        if not self.category:
            categories = list(set(response.css('#navcatlist a::attr("href")').re('(?<=category/).*')))
        else:
            categories = response.css('#navcatlist a::attr("href")').re('category/{0}'.format(self.category))
            if not categories:
                raise ValueError('invalid category slug. available slugs: \'%s\'' % "', '".join(categories))

        for category in categories:
            for page in range(self.start_page, self.end_page + 1):
                yield scrapy.Request('http://bhorerkagoj.net/online/' + category + '/page/{0}'.format(str(page)),
                                     callback=self.start_news_requests)

    def start_news_requests(self, response):
        news_links = list(set(response.css('.news-box h3 a::attr("href")').extract()))

        for link in news_links:
            yield self.make_requests_from_url(link)

    def parse_news(self, response):
        item = TextEntry()
        item['body'] = "".join(part for part in response.css('div.entry p::text').extract())
        return item
