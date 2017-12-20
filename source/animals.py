import scrapy
import requests
from bs4 import BeautifulSoup
import rdflib
import csv
import json

class AnimalItem(scrapy.Item):
    kingdom = scrapy.Field()
    phylum = scrapy.Field()


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://a-z-animals.com/animals']
    custom_settings = {
        'DOWNLOAD_DELAY': '0.25',
    }
    DOWNLOAD_DELAY = 0.25

    def parse(self, response):
        rows = response.xpath('//table[@class="az-facts"]/tr')
        d = {}
        header_name = response.xpath('//div[@id="container"]/main/article/header/h1/a/@title').extract()
        if header_name:
            d["header_name"] = header_name

        for row in rows:
            header = row.xpath('td/b/a/text()').extract()
            header2 = row.xpath('td/b/text()').extract()
            name = ''
            value = row.xpath('td/text()').extract()

            if header2:
                name = header2[0].replace(":", "")
            if header:
                name = header[0].replace(":", "")
            if value:
                value = value[0]
            if name and value:
                d[name] = value
        if d and 'Conservation Status' in d:
            yield d

        for name in response.css('div.content div.letter li'):
            next_page = name.css('a ::attr(href)').extract_first()
            if (next_page):
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
