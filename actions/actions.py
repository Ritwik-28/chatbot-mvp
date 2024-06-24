import os
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from neo4j import GraphDatabase
import wandb

# Initialize W&B
wandb.init(project="rasa-chatbot", entity="ritwikgupta28")

# Neo4j setup
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

neo4j_conn = Neo4jConnection("bolt://neo4j:7687", "neo4j", "qWeRtY2*")

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
        dispatcher.utter_message(text=f"Profile set for {name}. How can I assist you further?")
        return [SlotSet("user_profile", profile)]

class ActionQueryNeo4j(Action):
    def name(self) -> str:
        return "action_query_neo4j"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        query = tracker.latest_message.get('text')
        cypher_query = f"MATCH (n:Company) WHERE n.title CONTAINS '{query}' RETURN n"
        result = neo4j_conn.query(cypher_query)
        if result:
            result_text = "\n".join([str(record["n"]) for record in result])
            dispatcher.utter_message(text=result_text)
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
        if "profane" in user_message:
            dispatcher.utter_message(response="utter_profanity")
            return []

class ActionSaveConversation(Action):
    def name(self) -> str:
        return "action_save_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        name = tracker.get_slot("name")
        if name:
            directory = "User_Conversations"
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, f"{name}.json")
            save_conversation(tracker, file_path)
            dispatcher.utter_message(text="Your conversation has been saved.")
        else:
            dispatcher.utter_message(text="Name not provided. Cannot save conversation.")
        return []

def save_conversation(tracker, file_path):
    conversation = tracker.events
    with open(file_path, 'w') as f:
        json.dump(conversation, f, indent=4)