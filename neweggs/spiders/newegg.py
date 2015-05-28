# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import MapCompose, Compose, Join, TakeFirst

from neweggs.items import NeweggItem


class NeweggSpider(Spider):
    name = 'newegg'
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Product/ProductList.aspx?Submit=ENE&N=100021392&IsNodeId=1',
        'http://www.newegg.com/Game-Guides/SubCategory/ID-643',
        'http://www.newegg.com/Gaming/SubCategory/ID-3190',
        'http://www.newegg.com/Downloadable-Games/SubCategory/ID-438'
    ]

    def parse(self, response):
        for link in LinkExtractor(
            restrict_xpaths='//*[@class="itemCell"]//*[@class="itemDescription"]/..'
        ).extract_links(response):
            yield Request(link.url, callback=self.parse_details)
        
    def parse_details(self, response):
        l = ItemLoader(item=NeweggItem(), response=response)
        l.selector = Selector(response)
        l.add_xpath('title', '//h1/span[@itemprop="name"]/text()')
        
        l.add_xpath('image', '//script', re=r'"imageName":"([\d-]+.\w+)"')
        l.add_value('url', response.url)
        l.add_xpath('price', '//script', re=r"site_region:'(\w+)',")
        l.add_xpath('price', '//script', re=r"product_sale_price:\['(\d+.\d+)'\],")

        l.default_output_processor = TakeFirst()
        l.title_out = Compose(TakeFirst(), unicode.strip)            
        def build_image_url(filename):
            return 'http://images10.newegg.com/NeweggImage/productimage/' + filename
        l.image_out = Compose(TakeFirst(), build_image_url)
        l.price_out = Join(" ")
        
        
        yield l.load_item()