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
                "CREATE (n:Company {name: $name, description: $description, "
                "link: $link, course: $course})"
            )
            parameters = {
                "name": entry.get("name"),
                "description": entry.get("description"),
                "link": entry.get("link"),
                "course": entry.get("course")
            }
            neo4j_conn.query(query, parameters)

if __name__ == "__main__":
    neo4j_conn = Neo4jConnection("bolt://neo4j:7687", "neo4j", "test")
    load_data('company_data.json', neo4j_conn)
    neo4j_conn.close()