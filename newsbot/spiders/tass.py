import json
import re
from datetime import datetime
from urllib.parse import urlsplit

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig


class RussiaTassSpider(NewsSpider):
    name = "tass"
    start_urls = ["https://tass.ru/"]
    config = NewsSpiderConfig(
        title_path='_',
        date_path='_',
        date_format="%Y-%m-%d %H:%M:%S",
        text_path="div.text-content>div.text-block ::text",
        topics_path='_',
        authors_path='_',
        reposts_fb_path='_',
        reposts_vk_path='_',
        reposts_ok_path='_',
        reposts_twi_path='_',
        reposts_lj_path='_',
        reposts_tg_path='_',
        likes_path='_',
        views_path='_',
        comm_count_path='_'
    )
    custom_settings = {
        "DEPTH_LIMIT": 4,
        "DEPTH_STATS": True,
        "DEPTH_STATS_VERBOSE": True,
        "DOWNLOAD_DELAY": 10,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }
    category_le = LinkExtractor(restrict_css='ul.menu-sections-list>li>div.menu-sections-list__title-wrapper')

    def parse(self, response):
        for link in self.category_le.extract_links(response):
            yield scrapy.Request(url=link.url,
                                 priority=100,
                                 callback=self.parse_news_category,
                                 meta={}
                                 )

    def parse_news_category(self, response):
        news_section = response.css("section#news-list::attr(ng-init)").extract_first(default="")

        section_id = re.findall("sectionId\s+=\s+(.*?);", news_section)[0]
        exclude_ids = re.findall("excludeNewsIds\s*?=\s*?\'(.*)\';", news_section)[0]

        paging_data = {"sectionId": int(section_id),
                       "limit": 20,
                       "type": "",
                       "excludeNewsIds": exclude_ids,
                       "imageSize": 434, }
        yield self._create_api_request(paging_data, response.url)

    def _create_api_request(self, data, referer):
        return scrapy.Request(url="https://tass.ru/userApi/categoryNewsList",
                              method="POST",
                              body=json.dumps(data),
                              dont_filter=True,
                              headers={'Content-Type': 'application/json',
                                       'Referer': referer},
                              callback=self.parse_news_list,
                              meta={"data": data, "referer": referer})

    def parse_news_list(self, response):
        news_data = json.loads(response.body)
        last_time = news_data.get("lastTime", 0)
        data = response.meta["data"]
        referer = response.meta["referer"]
        data["timestamp"] = last_time
        yield self._create_api_request(data, referer)
        for news_item in news_data["newsList"]:
            url = response.urljoin(news_item["link"])
            yield scrapy.Request(url, callback=self.parse_document, meta={"news_item": news_item})

    def parse_document(self, response):
        news_item = response.meta["news_item"]
        url = response.url
        base_edition = urlsplit(self.start_urls[0])[1]
        edition = urlsplit(url)[1]

        l = ItemLoader(item=Document(), response=response)
        l.add_value('url', url)
        l.add_value('edition', '-' if edition == base_edition else edition)
        l.add_value('title', news_item["title"])
        l.add_value('topics', "")
        l.add_value('date', datetime.fromtimestamp(news_item["date"]).strftime(self.config.date_format))
        l.add_css('text', self.config.text_path)
        yield l.load_item()
