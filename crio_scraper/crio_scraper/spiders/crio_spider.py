import scrapy

class CrioSpider(scrapy.Spider):
    name = "crio_spider"
    allowed_domains = ["crio.do"]
    start_urls = ["https://www.crio.do/"]

    def parse(self, response):
        for content in response.css('div.content'):
            yield {
                'title': content.css('h1::text').get(),
                'body': content.css('p::text').getall(),
            }

        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)