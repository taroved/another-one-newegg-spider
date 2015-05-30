# -*- coding: utf-8 -*-
from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor

from neweggs.processors import NeweggProcessor


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

    image_tpl = 'http://images10.newegg.com/NeweggImage/productimage/%s'

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

        # turn the page
        if self.meta_page in response.meta:
            page = response.meta[self.meta_page] + 1
        else:
            page = 2
        # next list page
        if response.xpath('//*[@class="pagination "]//a[starts-with(@href,"javascript:Biz.Common.Pagination") and text()=%s]' % page):
            yield Request(response.meta[self.meta_url_tpl] % page, callback=self.parse_category,
                          meta={
                self.meta_page: page,
                self.meta_url_tpl: response.meta[self.meta_url_tpl]
            })

    def parse_details(self, response):
        """Parse product details into item.

        @url http://www.newegg.com/Product/Product.aspx?Item=N82E16832205158
        @returns items 1 1
        @scrapes title image url price
        """
        l = NeweggProcessor(response=response, image_tpl=self.image_tpl)
        l.selector = Selector(response)
        l.add_xpath('title', '//h1/span[@itemprop="name"]/text()')
        l.add_xpath('image', '//script', re=r'"imageName":"([\d-]+.\w+)"')
        l.add_value('url', response.url)
        l.add_xpath('price', '//script', re=r"site_currency:'(\w+)',")
        l.add_xpath(
            'price', '//script', re=r"product_sale_price:\['(\d+.\d+)'\],")

        yield l.load_item()
