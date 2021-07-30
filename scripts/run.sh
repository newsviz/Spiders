image=spiders:$(git rev-parse --abbrev-ref HEAD)
SOURCE=${2:-gazeta}
echo "scrap $SOURCE until $1"
docker run --rm -v $(pwd):/code -w /code/ $image bash -c "scrapy crawl $SOURCE -a until_date=$1"
# docker run --rm -it -v $(pwd):/code -w /code/ $image bash -c "scrapy shell https://www.gazeta.ru/sport/2021/02/08/a_13471844.shtml"
