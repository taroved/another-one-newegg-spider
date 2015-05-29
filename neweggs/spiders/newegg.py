# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Compose, Join, TakeFirst

from neweggs.items import NeweggItem


class NeweggSpider(Spider):
    name = 'newegg'
    allowed_domains = ['newegg.com']
    start_urls = [
        [
            'http://www.newegg.com/Game-Guides/SubCategory/ID-643',
            'http://www.newegg.com/Game-Guides/SubCategory/ID-643/Page-%s'
        ],
        [
            'http://www.newegg.com/Gaming/SubCategory/ID-3190',
            'http://www.newegg.com/Gaming/SubCategory/ID-3190/Page-%s'
        ],
        [
            'http://www.newegg.com/Downloadable-Games/SubCategory/ID-438',
            'http://www.newegg.com/Downloadable-Games/SubCategory/ID-438/Page-%s'
        ]
    ]
    
    image_url_tpl = 'http://images10.newegg.com/NeweggImage/productimage/%s'
    
    meta_page = 'newegg_spider_page'
    meta_url_tpl = 'newegg_url_template'
    
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url[0],  meta={self.meta_url_tpl: url[1]},
                          callback=self.parse_category)
    
    def parse_category(self, response):
        # parse list
        for link in LinkExtractor(
            restrict_xpaths='//*[@class="itemCell"]//*[@class="itemDescription"]/..'
        ).extract_links(response):
            yield Request(link.url, callback=self.parse_details)
            
        #turn the page
        if self.meta_page in response.meta:
            page = response.meta[self.meta_page] + 1
        else:
            page = 2
        #next list page
        if response.xpath('//*[@class="pagination "]//a[starts-with(@href,"javascript:Biz.Common.Pagination") and text()=%s]' % page):
            yield Request(response.meta[self.meta_url_tpl] % page, callback=self.parse_category,
                          meta={
                                self.meta_page: page,
                                self.meta_url_tpl: response.meta[self.meta_url_tpl] 
                                })
            
        
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
        l.image_out = Compose(TakeFirst(),
                              lambda x: self.image_url_tpl % x)
        l.price_out = Join(" ")
        
        yield l.load_item()