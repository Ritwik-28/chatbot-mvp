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

def load_company_data(file_path, neo4j_conn):
    with open(file_path, 'r') as file:
        data = json.load(file)
        for entry in data:
            query = (
                "CREATE (n:Company {name: $name, domain: $domain, description: $description, industry: $industry})"
            )
            parameters = {
                "name": entry.get("name"),
                "domain": entry.get("domain"),
                "description": entry.get("description"),
                "industry": entry.get("industry")
            }
            neo4j_conn.query(query, parameters)

def load_combined_output(file_path, neo4j_conn):
    with open(file_path, 'r') as file:
        data = json.load(file)
        for entry in data:
            query = (
                "CREATE (v:Video {youtube_url: $youtube_url, transcription: $transcription})"
            )
            parameters = {
                "youtube_url": entry.get("youtube_url"),
                "transcription": entry.get("transcription")
            }
            neo4j_conn.query(query, parameters)

if __name__ == "__main__":
    neo4j_conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "qWeRtY2*")
    load_company_data('company_data.json', neo4j_conn)
    load_combined_output('combined_output.json', neo4j_conn)
    neo4j_conn.close()