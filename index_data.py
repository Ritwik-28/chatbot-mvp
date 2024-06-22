from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch(['http://localhost:9200'])

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

if __name__ == "__main__":
    data = load_data()
    index_data(data)