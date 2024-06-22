from elasticsearch import Elasticsearch, helpers
import json

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

def load_data():
    with open('company_data.json') as f:
        data = json.load(f)
    return data

def index_data(data):
    actions = [
        {
            "_index": "company_data",
            "_source": record
        }
        for record in data
    ]
    helpers.bulk(es, actions)

if __name__ == "__main__":
    data = load_data()
    index_data(data)