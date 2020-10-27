from datetime import datetime

import lxml.html
import requests
import scrapy
from scrapy.linkextractors import LinkExtractor

from newsbot.spiders.news import NewsSpider, NewsSpiderConfig


class RiaSpider(NewsSpider):
    name = "ria"
    start_urls = ["https://www.ria.ru"]
    config = NewsSpiderConfig(
        title_path='//h1[contains(@class, "article__title")]/text()',
        date_path='//div[contains(@class, "endless__item")]/@data-published',
        date_format="%Y-%m-%dT%H:%MZ",
        text_path='//div[contains(@class, "article__block") and @data-type = "text"]//text()',
        topics_path='//a[contains(@class, "article__tags-item")]/text()',
        authors_path="_",
        reposts_fb_path="_",
        reposts_vk_path="_",
        reposts_ok_path="_",
        reposts_twi_path="_",
        reposts_lj_path="_",
        reposts_tg_path="_",
        likes_path='//span[contains(@class,"m-value")]/text()',
        views_path='//span[contains(@class,"statistic__item m-views")]/text()',
        comm_count_path="_",
    )
    news_le = LinkExtractor(restrict_css="div.lenta__item")

    def parse(self, response):
        article_links = self.news_le.extract_links(response)

        last_link = ""
        for link in article_links:
            last_link = link.url

            yield scrapy.Request(url=link.url, callback=self.parse_document)

        dt = self._get_last_dt_on_page(last_link)

        if datetime.strptime(dt, self.config.date_format).date() >= self.until_date:
            # Getting and forming the next page link
            next_page_link = response.xpath('//div[contains(@class, "lenta__item")]/@data-next').extract()[0]
            link_url = "{}{}".format(self.start_urls[0], next_page_link)

            yield scrapy.Request(
                url=link_url,
                priority=100,
                callback=self.parse,
                meta={"page_depth": response.meta.get("page_depth", 1) + 1},
            )

    def parse_document(self, response):
        for res in super().parse_document(response):
            # Leave only the last tag
            # (the last tag is always a global website tag)
            res["topics"] = [res["topics"][-1]]

            yield res

    def _get_last_dt_on_page(self, link):
        r = requests.get(link)
        source_code = r.text

        root = lxml.html.fromstring(source_code)

        dt = root.xpath(self.config.date_path)[0]

        return dt
