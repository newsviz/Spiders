from datetime import datetime

from scrapy import Request, Selector

from newsbot.spiders.news import NewsSpider, NewsSpiderConfig


class RussiaTassSpider(NewsSpider):
    name = "tass"
    start_urls = ["https://tass.ru/sitemap.xml"]
    config = NewsSpiderConfig(
        title_path='//div[contains(@class, "news-header__title")]//text() | '
        '//h1[contains(@class, "news-header__title")]//text()',
        date_path="//dateformat/@time",
        date_format="%Y-%m-%d %H:%M:%S",
        text_path='//div[contains(@class, "text-block")]//p//text()',
        topics_path="_",
        authors_path="_",
        reposts_fb_path="_",
        reposts_vk_path="_",
        reposts_ok_path="_",
        reposts_twi_path="_",
        reposts_lj_path="_",
        reposts_tg_path="_",
        likes_path="_",
        views_path="_",
        comm_count_path="_",
    )
    fields = [
        "title",
        "topics",
        "edition",
        "url",
        "text",
        "date",
    ]

    def parse(self, response):
        """Parse first main sitemap.xml by initial parsing method.
        Getting sub_sitemaps.
        """
        body = response.body
        links = Selector(text=body).xpath("//loc/text()").getall()
        last_modif_dts = Selector(text=body).xpath("//lastmod/text()").getall()

        for link, last_modif_dt in zip(links, last_modif_dts):
            last_modif_dt = datetime.strptime(last_modif_dt.replace(":", ""), "%Y-%m-%dT%H%M%S%z")

            if last_modif_dt.date() >= self.until_date:
                yield Request(url=link, callback=self.parse_sub_sitemap)

    def parse_sub_sitemap(self, response):
        body = response.body
        links = Selector(text=body).xpath("//loc/text()").getall()
        last_modif_dts = Selector(text=body).xpath("//lastmod/text()").getall()

        for link, last_modif_dt in zip(links, last_modif_dts):
            last_modif_dt = datetime.strptime(last_modif_dt.replace(":", ""), "%Y-%m-%dT%H%M%S%z")

            if last_modif_dt.date() >= self.until_date:
                yield Request(url=link, callback=self.parse_document)

    def parse_document(self, response):
        for res in super().parse_document(response):
            for field in self.fields:
                if field not in res:
                    res[field] = [""]

            res["text"] = [x.replace("\n", "\\n") for x in res["text"] if x != "\n"]
            res["title"] = [x.replace("\n", "\\n") for x in res["title"] if x != "\n"]

            try:
                pub_dt = int(res["date"][0])
                res["date"] = [str(datetime.fromtimestamp(pub_dt))]
            except KeyError:
                print("Error. No date value.")
            else:
                yield res
