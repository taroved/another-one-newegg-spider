# -*- coding: utf-8 -*-

# Scrapy settings for neweggs project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
DOWNLOAD_DELAY = 1

BOT_NAME = 'neweggs'

SPIDER_MODULES = ['neweggs.spiders']
NEWSPIDER_MODULE = 'neweggs.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'neweggs (+http://www.yourdomain.com)'
