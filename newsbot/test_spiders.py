import codecs

import pytest
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

from newsbot.spiders.gazeta import GazetaSpider
from newsbot.spiders.interfax import InterfaxSpider
from newsbot.spiders.iz import IzSpider
from newsbot.spiders.kommersant import KommersantSpider
from newsbot.spiders.meduza import MeduzaSpider
from newsbot.spiders.news import NewsSpider
from newsbot.spiders.rbc import RbcSpider
from newsbot.spiders.ria import RiaSpider
from newsbot.spiders.rt import RussiaTodaySpider
from newsbot.spiders.tass import RussiaTassSpider
from newsbot.spiders.tvzvezda import TvZvezdaSpider
from newsbot.spiders.vedomosti import VedomostiSpider

PAGE_MAX = 5


def _run_crawler(spider_cls):
    """
    spider_cls: Scrapy Spider class
    settings: Scrapy settings
    returns: Twisted Deferred
    """
    settings = get_project_settings()
    settings['CLOSESPIDER_PAGECOUNT'] = PAGE_MAX
    runner = CrawlerRunner(settings)
    return runner.crawl(spider_cls)


def has_lines_except_header(filename):
    file = codecs.open(filename, 'r', 'utf-8')
    lines = file.readlines()
    file.close()
    return len(lines) > 1


@pytest.mark.parametrize('name, cls',
                         [('gazeta', GazetaSpider),
                          ('interfax', InterfaxSpider),
                          ('iz', IzSpider),
                          ('kommersant', KommersantSpider),
                          ('meduza', MeduzaSpider),
                          ('news', NewsSpider),
                          ('rbc', RbcSpider),
                          ('ria', RiaSpider),
                          ('rt', RussiaTodaySpider),
                          ('tass', RussiaTassSpider),
                          ('tvzvezda', TvZvezdaSpider),
                          ('vedomosti', VedomostiSpider)])
def test_spider(name, cls):
    deferred = _run_crawler(cls)

    @deferred.addCallback
    def _success(results):
        assert has_lines_except_header(f'{name}.csv')

    @deferred.addErrback
    def _error(failure):
        raise failure.value

    return deferred
