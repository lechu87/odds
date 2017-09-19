import scrapy_test
from lxml import html
import requests


class QuotesSpider(scrapy_test.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'https://www.efortuna.pl/pl/strona_glowna/serwis_sportowy/liga_mistrzow/index.html'
        ]
        for url in urls:
            yield scrapy_test.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

page = requests.get('https://www.efortuna.pl/pl/strona_glowna/serwis_sportowy/liga_mistrzow/index.html')
tree = html.fromstring(page.content)
games = tree.xpath('//div[@title="buyer-name"]/text()')


print(tree)