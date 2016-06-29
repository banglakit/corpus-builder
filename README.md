# banglakit/corpus-builder

Having a large enough set of text is essential for NLP tasks; this tool is designed for the sole purpose of building large collection of text documents from the web.

A practical understanding of Python and [Scrapy](http://www.scrapy.org) is essential for using the tool.

### Example Usage
```bash
scrapy crawl bangladesh_pratidin -a start_date='2016-06-01' -a end_date='2016-06-05' -o test3.csv
```
