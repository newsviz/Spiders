# Spiders
Spiders and crawlers for news download

# Contributing
См [CONTRIBUTING.md](CONTRIBUTING.md)

### Запуск паука ###

```
scrapy crawl <название паука> -a until_date=DD.MM.YYYY
```

Например, запуск паука для сайта `gazeta.ru` можно сделать так:
```
scrapy crawl gazeta -a until_date=01.01.1980
```
Такой запуск будет искать все статьи с сайта с текущего дня до 1 января 1980 года.

_(название паука задается в свойстве `name` класса паука)_

Также удобно сохранять логи паука в файл с помощью параметра `--logfile` (опционально):
```
scrapy crawl gazeta -a until_date=01.01.1980 --logfile gazeta.log
```

### Написание нового паука ###

Можно взять любого существующего в `newsbot/spiders` паука за основу.

Общая структура паука примерно такая:

```
class CoolWebsiteSpider(NewsSpider):
    name = 'cool_website'  # название паука для использования при вызове scrapy (scrapy crawl cool_website)
    start_urls = ['https://www.cool_website.com']  # стартовая страница; ответ с этой страницы придет в функцию parse

    config = NewsSpiderConfig(
        # XPath пути...
        title_path='<xpath_to_title>',  # до названия статьи
        date_path='<xpath_to_title>',  # до даты статьи
        date_format='%Y-%m-%dT%H:%M:%S',  # формат даты, собираемой в <date_path>
        text_path='<xpath_to_title>',  # до текста статьи
        topics_path='<xpath_to_title>',  # до тем статьи
        authors_path='<xpath_to_title>',  # до авторов статьи
        reposts_fb_path='_',  # до количества репостов в Facebook
        reposts_vk_path='_',  # до количества репостов во Вконтакте
        reposts_ok_path='_',  # до количества репостов в Одноклассниках
        reposts_twi_path='_',  # до количества репостов в Twitter
        reposts_lj_path='_',  # до количества репостов в LifeJournal
        reposts_tg_path='_',  # до количества репостов в Одноклассниках
        likes_path='_',  # до количества лайков статьи
        views_path='_',  # до количества просмотров статьи
        comm_count_path='_'  # до количества комментариев статьи
    )

    # Функция, которая будет вызвана для парсинга "start_urls"
    # Здесь обычно стоит
    # - взять все ссылки на новости, вызвать для каждой:
    #   yield Request(url=article_link, callback=self.parse_document)
    # - сформировать ссылку для следующей страницы с новостями (в случае с пагинацией)
    # - вызвать для новой страницы этот же метод "parse"
    #   yield Request(url=page_link, callback=self.parse)
    def parse(self, response):
        ...

    # Метод, который переопределяет метод "" из родительского класса "NewsSpider"
    # Переопределять его нужно, если нужно произвести специфичные для веб-сайта преобразования
    # над получаемыми данными: убрать рекламные блоки из текста, привести дату-время к нужному виду и т.п.
    def parse_document(self, response):
        # Сначала вызываем парсинг в родительском классе
        for res in super().parse_document(response):
            # Делаем специфичные преобразования
            # Например, убираем ":" из тайм-зоны
            pub_dt = res['date'][0]
            res['date'] = [pub_dt[:-3] + pub_dt[-3:].replace(':', '')]

            # Возвращаем результат - он пойдет в NewsbotPipeline.process_item в newsbot/pipelines.py
            yield res
```

Что стоит сделать, когда берешься за написание нового паука:
1) Скопипастить код другого паука :)
2) Поменять название класса на релевантный сайту
3) Поменять `name` на релевантный сайту
4) Сделать другой стартовый url
5) Прописать в `NewsSpiderConfig` нужные пути до элементов сайта, посмотрев исходный код страниц сайта
6) Изменить `parse` и, если необходимо, `parse_document`
7) Тестировать

### Тестирование

Для автоматического тестирования пауков запустите команду

`pytest newsbot/test_spiders.py`

После завершения тестирования в short test summary info будут выведены пауки, непрошедшие тесты.

### Рекомендации

1) Заглядывайте в теги `<meta>` - иногда оттуда можно легко достать даты публикаций, топики статей, авторов и пр.
2) Если собираете данные, сделайте это в `newsbot/settings.py`, чтобы ускорить процесс сбора:  
    - `CONCURRENT_REQUESTS = 500  # поставьте больше параллельных запросов`
    - `LOG_LEVEL = 'INFO'  # поставьте меньше уровень логирования (во избежание большого лог-файла)`
    - `DOWNLOAD_DELAY = 0.25  # поставьте поменьше задержку между запросами`
