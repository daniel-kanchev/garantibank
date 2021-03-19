import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from garantibank.items import Article


class GarantibankSpider(scrapy.Spider):
    name = 'garantibank'
    start_urls = ['https://www.garantibank.de/ueber-uns/newsuebersicht']

    def parse(self, response):
        yield response.follow(response.url, self.parse_page, dont_filter=True)

        next_pages = response.xpath('//ul[@class="pages"]/li/a/@href').getall()
        yield from response.follow_all(next_pages, self.parse_page)

    def parse_page(self, response):
        links = response.xpath('//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//em/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="news-box"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
