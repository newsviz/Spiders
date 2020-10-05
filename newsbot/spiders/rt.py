from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy import Request, Selector

from typing import List
from datetime import date


class RussiaTodaySpider(NewsSpider):
    name = 'rt'

    start_urls = ['https://russian.rt.com/sitemap.xml']

    config = NewsSpiderConfig(
        title_path='//h1/text()',
        date_path='//meta'
        '[contains(@name, "mediator_published_time")]/@content',
        date_format="%Y-%m-%dT%H:%M:%S",
        text_path='//div[contains(@class, "article__text")]//text()',
        topics_path='//meta[contains(@name, "mediator_theme")]/@content',
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

    def parse(self, response):
        """Parse first main sitemap.xml by initial parsing method.
        Getting sub_sitemaps.
        """
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()

        for link in links:
            yield Request(url=link,
                          callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        """Parse each sub_sitemap.
        """
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()

        for link in links:
            yield Request(url=link,
                          callback=self.parse_document)

    def _fix_syntax(self, sample: List[str], idx_split: int) -> List[str]:
        """Fix timestamp syntax, droping timezone postfix.
        """
        sample = [sample[0][:idx_split]]
        return sample

    def _get_date(self, lst: List[str]):
        """Convert list into date obj.
        """
        y, m, d = [int(num) for num in lst]
        return date(y, m, d)

    def parse_document(self, response):
        """Final parsing method.
        Parse each article."""
        for item in super().parse_document(response):

            # Try to drop timezone postfix.
            try:
                item['date'] = self._fix_syntax(item['date'], -6)
            except KeyError:
                print('Error. No date value.')
            else:
                raw_date = item['date'][0][:10].split('-')
                processed_date = self._get_date(raw_date)

                if processed_date >= self.until_date:
                    yield item
