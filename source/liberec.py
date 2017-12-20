import scrapy
import requests
from bs4 import BeautifulSoup
import rdflib
import csv
import json
import unicodedata
import string

class AnimalItem(scrapy.Item):
    kingdom = scrapy.Field()
    phylum = scrapy.Field()


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    url = 'https://www.zooliberec.cz/zvirata-u-nas.html?page=1'
    start_urls = ['https://www.zooliberec.cz/zvirata-u-nas.html?page=1']
    custom_settings = {
        'DOWNLOAD_DELAY': '0.25',
    }
    DOWNLOAD_DELAY = 0.25
    page = 1

    def parse(self, response):
        d = {}

        latin_name = response.xpath('//div[@class="latinTitle"]/strong/text()').extract()
        if latin_name:
            d["latin_name"] = latin_name

        eng_name = response.xpath('//div[@class="engTitle"]/strong/text()').extract()
        if eng_name:
            d["eng_name"] = eng_name

        name = response.xpath('//div[@class="col-xs-12 col-sm-8 col-md-9"]/h1/text()').extract()
        if name:
            d["name"] = name
            uri_name = name[0].lower()
            uri_name = unicodedata.normalize("NFKD", uri_name)
            d["uri_name"] = uri_name.encode("ascii", "ignore").replace(" ", "-")+".html"

        rows = response.xpath('//ul[@class="parametersLists"]/li')
        for row in rows:
            header = row.xpath('span/text()').extract()
            name = ''
            value = row.xpath('strong/text()').extract()
            if header:
                name = header[0].replace(":", "")
            if value:
                value = value[0]

            if name and value:
                d[name] = value
        if d:
            yield d

        for name in response.css('div.articleBg div.row div.my-col-sx'):
            next_page = name.css('a ::attr(href)').extract_first()
            if (next_page):
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

        if self.page < 10:
            self.page += 1
            yield scrapy.Request(response.urljoin(self.url[:-1] + str(self.page)), callback=self.parse)
