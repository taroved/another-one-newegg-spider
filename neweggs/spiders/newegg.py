# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import MapCompose, Compose, Join

from neweggs.items import NeweggItem


class NeweggSpider(CrawlSpider):
    name = 'newegg'
    allowed_domains = ['newegg.com']
    start_urls = ['http://www.newegg.com/Digital-Games/Category/ID-377']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//*[@id="blaNavigation"]'),
             callback='parse_category'),
    )

    def parse_category(self, response):
        import pdb
        pdb.set_trace()
        for link in LinkExtractor(
            restrict_xpaths='//*[@class="itemCell"]//*[@class="itemDescription"]/..'
        ).extract_links(response):
            yield Request(link.url, callback=self.parse_details)
        
    def parse_details(self, response):
        l = ItemLoader(item=NeweggItem(), response=response)
        l.selector = Selector(response)
        l.add_xpath('title', '//h1/span[@itemprop="name"]')
        l.add_xpath('image', '//script', re=r'"imageName":"([\d-]+.\w+)"')
        
        def build_image_url(filename):
            return 'http://images10.newegg.com/NeweggImage/productimage/' + filename
        l.image_in(MapCompose(build_image_url))
        
        l.add_value('url', response.url)
        l.add_xpath('price', '//*[@id="singleFinalPrice"]')
        
        def build_price(text):
            return text
        
        l.price_in(Compose(Join, build_image_url))
        
        yield l.load_item()