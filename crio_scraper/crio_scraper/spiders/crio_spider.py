import scrapy
from scrapy.spiders import SitemapSpider
from scrapy.crawler import CrawlerProcess
import os

class CrioSitemapSpider(SitemapSpider):
    name = 'crio_sitemap_spider'
    allowed_domains = ['crio.do']
    sitemap_urls = ['https://www.crio.do/sitemap.xml']  # URL to the sitemap

    def parse(self, response):
        self.log(f"Visited {response.url}")
        
        # Adjust selectors based on the page structure
        title = response.css('h1::text').get()
        body = response.css('p::text').getall()

        self.log(f"Found title: {title}")
        self.log(f"Found body: {body}")

        if title or body:
            yield {
                'url': response.url,
                'title': title,
                'body': body,
            }

def run_sitemap_spider():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(repo_root, "company_data.json")

    # Print the output file path to verify
    print(f"Output file will be saved to: {output_file}")

    process = CrawlerProcess(settings={
        'FEEDS': {
            output_file: {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
            },
        },
        'LOG_LEVEL': 'DEBUG',  # Set log level to DEBUG to see all messages
    })

    process.crawl(CrioSitemapSpider)
    process.start()

    # Verify if the file was created
    if os.path.exists(output_file):
        print(f"File successfully created at: {output_file}")
    else:
        print(f"File was not created at: {output_file}")

# Run the function to scrape and create the JSON file
if __name__ == "__main__":
    run_sitemap_spider()
