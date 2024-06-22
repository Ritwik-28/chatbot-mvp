import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from elasticsearch import Elasticsearch
import wandb
import scrapy
from scrapy.crawler import CrawlerProcess
import json

# Initialize W&B
wandb.init(project="rasa-chatbot", entity="ritwikgupta28")

# Elasticsearch setup
es = Elasticsearch(['http://elasticsearch:9200'])

class ActionSetProfile(Action):
    def name(self) -> str:
        return "action_set_profile"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        name = tracker.get_slot("name")
        email = tracker.get_slot("email")
        phone_number = tracker.get_slot("phone_number")
        profile = f"Name: {name}, Email: {email}, Phone Number: {phone_number}"
        # Save profile to the backend
        dispatcher.utter_message(text=f"Profile set for {name}. How can I assist you further?")
        return [SlotSet("user_profile", profile)]

class ActionQueryElasticsearch(Action):
    def name(self) -> str:
        return "action_query_elasticsearch"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        query = tracker.latest_message.get('text')
        response = es.search(index="company_data", body={"query": {"match": {"content": query}}})
        hits = response['hits']['hits']
        if hits:
            answer = hits[0]['_source']['content']
            dispatcher.utter_message(text=answer)
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find any information on that topic.")
        return []

class ActionDetectProfanity(Action):
    def name(self) -> str:
        return "action_detect_profanity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        user_message = tracker.latest_message.get('text')
        # Here you can use a profanity detection library or API
        # For demonstration, let's assume a simple check
        if "profane" in user_message:  # Simple check for demonstration
            dispatcher.utter_message(response="utter_profanity")
            return []
        return []

class ActionScrapeWebsite(Action):
    def name(self) -> str:
        return "action_scrape_website"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

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

        process = CrawlerProcess(settings={
            "FEEDS": {
                "company_data.json": {"format": "json"},
            },
        })

        process.crawl(CrioSpider)
        process.start()  # the script will block here until the crawling is finished

        # Once crawling is done, index the data
        def load_data():
            with open('company_data.json') as f:
                data = json.load(f)
            return data

        def index_data(data):
            actions = [
                {
                    "_index": "company_data",
                    "_type": "_doc",
                    "_id": i,
                    "_source": data[i]
                }
                for i in range(len(data))
            ]
            helpers.bulk(es, actions)

        data = load_data()
        index_data(data)

        dispatcher.utter_message(text="Website data has been scraped and indexed.")
        return []