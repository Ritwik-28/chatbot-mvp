import json
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

def load_data(file_path, neo4j_conn):
    with open(file_path, 'r') as file:
        data = json.load(file)
        for entry in data:
            query = (
                "CREATE (n:Company {title: $title, body: $body})"
            )
            parameters = {
                "title": entry.get("title"),
                "body": " ".join(entry.get("body"))
            }
            neo4j_conn.query(query, parameters)

if __name__ == "__main__":
    neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "qWeRtY2*")
    load_data('company_data.json', neo4j_conn)
    neo4j_conn.close()