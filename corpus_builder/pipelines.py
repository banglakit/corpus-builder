# -*- coding: utf-8 -*-

from breadability.readable import Article


class ContentExtractorPipeline(object):
    def process_item(self, item, spider):
    	# getting item as HTMLResponseBody
    	document = Article(item.get(body, ""))
    	item['body'] = "".join([text for text in document.readable_dom.itertext()])

        return output_item
