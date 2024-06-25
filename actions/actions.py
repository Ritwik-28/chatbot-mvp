import os
import json
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from neo4j import GraphDatabase

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

class ActionGreetAndLead(Action):
    def name(self) -> Text:
        return "action_greet_and_lead"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Check if user profile exists
        user_profile = tracker.get_slot("user_profile")
        if user_profile:
            dispatcher.utter_message(response="utter_greet")
            dispatcher.utter_message(text=f"Welcome back! I remember you from our previous conversation.")
            return []
        else:
            dispatcher.utter_message(response="utter_greet")
            dispatcher.utter_message(text="I'd like to learn more about you. May I ask you a few questions?")
            return [FollowupAction("lead_form")]

class ActionSetProfile(Action):
    def name(self) -> Text:
        return "action_set_profile"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
        email = tracker.get_slot("email")
        phone_number = tracker.get_slot("phone_number")
        interest = tracker.get_slot("interest")
        
        profile = {
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "interest": interest
        }
        
        # Here you might want to save this profile to a database
        
        dispatcher.utter_message(text=f"Thank you, {name}. I've set up your profile with the following information:")
        dispatcher.utter_message(text=f"Email: {email}")
        dispatcher.utter_message(text=f"Phone: {phone_number}")
        dispatcher.utter_message(text=f"Interest: {interest}")
        dispatcher.utter_message(text="How can I assist you further?")
        
        return [SlotSet("user_profile", profile)]

class ActionQueryNeo4j(Action):
    def name(self) -> Text:
        return "action_query_neo4j"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        query = tracker.latest_message.get('text')
        cypher_query = f"MATCH (n:Company) WHERE n.title CONTAINS '{query}' RETURN n.title, n.description LIMIT 5"
        result = neo4j_conn.query(cypher_query)
        if result:
            dispatcher.utter_message(text="Here's what I found:")
            for record in result:
                dispatcher.utter_message(text=f"Company: {record['n.title']}")
                dispatcher.utter_message(text=f"Description: {record['n.description']}")
        else:
            dispatcher.utter_message(text="I'm sorry, I couldn't find any information on that topic in our database.")
        return []

class ActionDetectProfanity(Action):
    def name(self) -> Text:
        return "action_detect_profanity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text', '').lower()
        # This is a very basic profanity filter. In a real application, you'd want a more comprehensive list
        profanity_list = ['damn', 'hell', 'shit', 'fuck']
        if any(word in user_message for word in profanity_list):
            dispatcher.utter_message(response="utter_profanity_warning")
            return [SlotSet("profanity_used", True)]
        return [SlotSet("profanity_used", False)]

class ActionSaveConversation(Action):
    def name(self) -> Text:
        return "action_save_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
        if name:
            directory = "User_Conversations"
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, f"{name}_{tracker.sender_id}.json")
            save_conversation(tracker, file_path)
            dispatcher.utter_message(text="Your conversation has been saved. You can refer to it later if needed.")
        else:
            dispatcher.utter_message(text="I'm sorry, but I need your name to save the conversation. Can you provide it?")
            return [FollowupAction("lead_form")]
        return []

def save_conversation(tracker, file_path):
    conversation = []
    for event in tracker.events:
        if event.get("event") == "user":
            conversation.append({"user": event.get("text")})
        elif event.get("event") == "bot":
            conversation.append({"bot": event.get("text")})
    with open(file_path, 'w') as f:
        json.dump(conversation, f, indent=4)

class ActionHandoff(Action):
    def name(self) -> Text:
        return "action_handoff"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="I understand that you'd like to speak with a human agent.")
        dispatcher.utter_message(text="I'm transferring you now. Please note that our agents are available Monday to Friday, 9 AM to 5 PM EST.")
        dispatcher.utter_message(text="If it's outside these hours, an agent will contact you as soon as possible.")
        # Here you would typically integrate with your customer service platform
        # For this example, we'll just set a slot to indicate the handoff was requested
        return [SlotSet("handoff_requested", True)]

class ActionProvideCourseDetails(Action):
    def name(self) -> Text:
        return "action_provide_course_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        interest = tracker.get_slot("interest")
        if interest:
            if interest.lower() == "qa automation":
                dispatcher.utter_message(text="Our QA Automation course covers:")
                dispatcher.utter_message(text="1. Introduction to Test Automation")
                dispatcher.utter_message(text="2. Selenium WebDriver")
                dispatcher.utter_message(text="3. TestNG Framework")
                dispatcher.utter_message(text="4. Jenkins for Continuous Integration")
                dispatcher.utter_message(text="Duration: 12 weeks")
                dispatcher.utter_message(text="Price: $1999")
            elif interest.lower() == "software development":
                dispatcher.utter_message(text="Our Software Development course covers:")
                dispatcher.utter_message(text="1. Programming Fundamentals (Python)")
                dispatcher.utter_message(text="2. Web Development (HTML, CSS, JavaScript)")
                dispatcher.utter_message(text="3. Backend Development (Node.js, Express)")
                dispatcher.utter_message(text="4. Database Management (SQL, MongoDB)")
                dispatcher.utter_message(text="Duration: 16 weeks")
                dispatcher.utter_message(text="Price: $2499")
            else:
                dispatcher.utter_message(text=f"I'm sorry, but I don't have information about courses related to {interest}.")
                dispatcher.utter_message(text="Would you be interested in QA Automation or Software Development?")
        else:
            dispatcher.utter_message(text="I'm not sure what course you're interested in. Can you tell me if you're looking for information about QA Automation or Software Development?")
        return []