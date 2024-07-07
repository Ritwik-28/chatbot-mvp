import re
import socket
import os
import wandb
import openai
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from neo4j import GraphDatabase

# Initialize wandb
wandb.init(project="rasa-chatbot", entity="ritwikgupta28")

# Function to get the IP address
def get_ip():
    IS_CODESPACE = os.getenv("CODESPACES") == "true"
    if IS_CODESPACE:
        # Use environment variable specific to Codespaces for Neo4j IP
        ip_address = os.getenv("CODESPACE_HOST")
    else:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
    return ip_address

# Neo4j setup with dynamic IP address
neo4j_ip = get_ip()
neo4j_uri = f"bolt://{neo4j_ip}:7687"
neo4j_user = "neo4j"
neo4j_password = "qWeRtY2*"  # Hardcoded password

# OpenAI API Key
OPENAI_API_KEY = "your-openai-api-key"
openai.api_key = OPENAI_API_KEY

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

neo4j_conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)

def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant with knowledge about Crio."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        wandb.log({"error": str(e)})
        return "I'm sorry, I couldn't process your request at the moment."

def get_text_embedding(text):
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0]['embedding']
    except Exception as e:
        wandb.log({"error": str(e)})
        return None

class ActionGreetAndLead(Action):
    def name(self) -> Text:
        return "action_greet_and_lead"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            wandb.log({"action": "greet_and_lead"})
            dispatcher.utter_message(text="Hi, I'm Crio Beaver, here to help you through your learning journey. What led you to browse through Crio?")
            dispatcher.utter_message(buttons=[
                {"payload": "/want_upskill", "title": "I want to upskill"},
                {"payload": "/looking_for_job", "title": "I am looking for a job"}
            ])
            return []
        except Exception as e:
            wandb.log({"error": str(e)})
            dispatcher.utter_message(text="Sorry, something went wrong while processing your request.")
            return []

class ActionCaptureLead(Action):
    def name(self) -> Text:
        return "action_capture_lead"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        wandb.log({"action": "capture_lead", "intent": intent})

        if intent in ["want_upskill", "looking_for_job"]:
            dispatcher.utter_message(text="Thanks for sharing that. Before we dive deeper, I'd like to get to know you better. Could you please tell me your name?")
            return [SlotSet("user_intent", intent), FollowupAction("action_capture_name")]
        else:
            dispatcher.utter_message(text="I'm not sure I understand. Are you looking to upskill or find a job?")
            return [FollowupAction("action_greet_and_lead")]

class ActionCaptureName(Action):
    def name(self) -> Text:
        return "action_capture_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = next(tracker.get_latest_entity_values("name"), None)
        wandb.log({"action": "capture_name", "name": name})
        if name:
            dispatcher.utter_message(text=f"Nice to meet you, {name}! Could you also share your email address? This will help us keep in touch and provide you with relevant information.")
            return [SlotSet("name", name), FollowupAction("action_capture_email")]
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't catch your name. Could you please tell me your name?")
            return [FollowupAction("action_capture_name")]

class ActionCaptureEmail(Action):
    def name(self) -> Text:
        return "action_capture_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        email = next(tracker.get_latest_entity_values("email"), None)
        wandb.log({"action": "capture_email", "email": email})
        if email and self.is_valid_email(email):
            name = tracker.get_slot("name")
            dispatcher.utter_message(text=f"Great, thank you {name}. One last thing - what's the best phone number to reach you?")
            return [SlotSet("email", email), FollowupAction("action_capture_phone")]
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't catch a valid email address. Could you please provide a valid email address?")
            return [FollowupAction("action_capture_email")]

    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

class ActionCapturePhone(Action):
    def name(self) -> Text:
        return "action_capture_phone"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        phone = next(tracker.get_latest_entity_values("phone"), None)
        wandb.log({"action": "capture_phone", "phone": phone})
        if phone and self.is_valid_phone(phone):
            name = tracker.get_slot("name")
            dispatcher.utter_message(text=f"Thank you for providing your details, {name}. Now, let's explore how Crio can help you.")
            return [SlotSet("phone", phone), FollowupAction("action_profile_user")]
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't catch a valid phone number. Could you please provide a valid phone number?")
            return [FollowupAction("action_capture_phone")]

    def is_valid_phone(self, phone):
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None

class ActionProfileUser(Action):
    def name(self) -> Text:
        return "action_profile_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_intent = tracker.get_slot("user_intent")
        wandb.log({"action": "profile_user", "user_intent": user_intent})
        if user_intent == "looking_for_job":
            return self.profile_job_seeker(dispatcher, tracker)
        elif user_intent == "want_upskill":
            return self.profile_upskiller(dispatcher, tracker)
        else:
            dispatcher.utter_message(text="I'm not sure what you're looking for. Could you please clarify if you're looking for a job or want to upskill?")
            return [FollowupAction("action_greet_and_lead")]

    def profile_job_seeker(self, dispatcher, tracker):
        dispatcher.utter_message(text="I understand you're looking for a job. Let's get some more information to help you better.")
        dispatcher.utter_message(text="What's your current work status?")
        dispatcher.utter_message(buttons=[
            {"payload": "/cwp", "title": "Currently Working"},
            {"payload": "/nwp", "title": "Not Working"},
            {"payload": "/student", "title": "Student"}
        ])
        return [FollowupAction("action_handle_work_status")]

    def profile_upskiller(self, dispatcher, tracker):
        dispatcher.utter_message(text="Great to hear you want to upskill! What area are you most interested in developing?")
        dispatcher.utter_message(buttons=[
            {"payload": "/interest_qa_automation", "title": "QA Automation"},
            {"payload": "/interest_software_development", "title": "Software Development"}
        ])
        return [FollowupAction("action_handle_upskill_interest")]

class ActionHandleWorkStatus(Action):
    def name(self) -> Text:
        return "action_handle_work_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        work_status = tracker.latest_message['intent'].get('name')
        wandb.log({"action": "handle_work_status", "work_status": work_status})
        if work_status == "cwp":
            return self.handle_cwp(dispatcher, tracker)
        elif work_status == "nwp":
            return self.handle_nwp(dispatcher, tracker)
        elif work_status == "student":
            return self.handle_student(dispatcher, tracker)
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't understand your work status. Could you please select one of the options?")
            return [FollowupAction("action_profile_user")]

    def handle_cwp(self, dispatcher, tracker):
        dispatcher.utter_message(text="What's your current company name and designation?")
        return [SlotSet("work_status", "cwp"), FollowupAction("action_capture_company_details")]

    def handle_nwp(self, dispatcher, tracker):
        dispatcher.utter_message(text="I see that you're currently not working. When did you last work, and what was your role?")
        return [SlotSet("work_status", "nwp"), FollowupAction("action_capture_previous_job")]

    def handle_student(self, dispatcher, tracker):
        dispatcher.utter_message(text="As a student, what degree are you pursuing and when do you expect to graduate?")
        return [SlotSet("work_status", "student"), FollowupAction("action_capture_student_details")]

class ActionHandleUpskillInterest(Action):
    def name(self) -> Text:
        return "action_handle_upskill_interest"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        interest = tracker.latest_message['intent'].get('name')
        wandb.log({"action": "handle_upskill_interest", "interest": interest})
        if interest in ["interest_qa_automation", "interest_software_development"]:
            return self.provide_course_info(dispatcher, tracker, interest)
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't understand your interest. Could you please select one of the options?")
            return [FollowupAction("action_profile_user")]

    def provide_course_info(self, dispatcher, tracker, interest):
        interest_area = "QA Automation" if interest == "interest_qa_automation" else "Software Development"
        dispatcher.utter_message(text=f"Great choice! Our {interest_area} program is designed to give you hands-on experience and make you job-ready.")
        dispatcher.utter_message(text="Would you like to know more about the curriculum or the career opportunities after completing this program?")
        dispatcher.utter_message(buttons=[
            {"payload": "/curriculum_info", "title": "Curriculum"},
            {"payload": "/career_info", "title": "Career Opportunities"}
        ])
        return [SlotSet("interest_area", interest_area)]

class ActionCaptureCompanyDetails(Action):
    def name(self) -> Text:
        return "action_capture_company_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        company = next(tracker.get_latest_entity_values("company"), None)
        designation = next(tracker.get_latest_entity_values("designation"), None)
        wandb.log({"action": "capture_company_details", "company": company, "designation": designation})
        if company and designation:
            dispatcher.utter_message(text=f"Thank you for sharing that you work at {company} as a {designation}.")
            return [SlotSet("company", company), SlotSet("designation", designation), FollowupAction("action_handle_upskill_interest")]
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't catch your company name or designation. Could you please provide both?")
            return [FollowupAction("action_capture_company_details")]

class ActionCapturePreviousJob(Action):
    def name(self) -> Text:
        return "action_capture_previous_job"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_job = next(tracker.get_latest_entity_values("last_job"), None)
        last_role = next(tracker.get_latest_entity_values("last_role"), None)
        wandb.log({"action": "capture_previous_job", "last_job": last_job, "last_role": last_role})
        if last_job and last_role:
            dispatcher.utter_message(text=f"I see that you previously worked at {last_job} as a {last_role}. Thank you for sharing.")
            return [SlotSet("last_job", last_job), SlotSet("last_role", last_role), FollowupAction("action_handle_upskill_interest")]
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't catch your previous job details. Could you please provide your last company and role?")
            return [FollowupAction("action_capture_previous_job")]

class ActionCaptureStudentDetails(Action):
    def name(self) -> Text:
        return "action_capture_student_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        degree = next(tracker.get_latest_entity_values("degree"), None)
        graduation_year = next(tracker.get_latest_entity_values("graduation_year"), None)
        wandb.log({"action": "capture_student_details", "degree": degree, "graduation_year": graduation_year})
        if degree and graduation_year:
            dispatcher.utter_message(text=f"Got it, you're pursuing a {degree} and expecting to graduate in {graduation_year}.")
            return [SlotSet("degree", degree), SlotSet("graduation_year", graduation_year), FollowupAction("action_handle_upskill_interest")]
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't catch your degree or graduation year. Could you please provide both?")
            return [FollowupAction("action_capture_student_details")]

class ActionHandoff(Action):
    def name(self) -> Text:
        return "action_handoff"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        wandb.log({"action": "handoff"})
        dispatcher.utter_message(text="I understand you'd like to speak with a human. I'm transferring you to one of our representatives now.")
        # Here you would implement the logic to transfer to a human operator
        # For example, you might send an email or create a ticket in your CRM system
        return []

class ActionSaveConversation(Action):
    def name(self) -> Text:
        return "action_save_conversation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        conversation = tracker.events
        wandb.log({"action": "save_conversation", "conversation": conversation})

        # Save conversation to Neo4j
        try:
            user_id = tracker.sender_id
            name = tracker.get_slot("name")
            email = tracker.get_slot("email")
            phone = tracker.get_slot("phone")
            user_intent = tracker.get_slot("user_intent")
            interest_area = tracker.get_slot("interest_area")
            work_status = tracker.get_slot("work_status")
            company = tracker.get_slot("company")
            designation = tracker.get_slot("designation")
            last_job = tracker.get_slot("last_job")
            last_role = tracker.get_slot("last_role")
            degree = tracker.get_slot("degree")
            graduation_year = tracker.get_slot("graduation_year")

            # Create a Neo4j query to save the conversation data
            query = """
            MERGE (u:User {user_id: $user_id})
            SET u.name = $name, 
                u.email = $email, 
                u.phone = $phone, 
                u.user_intent = $user_intent, 
                u.interest_area = $interest_area, 
                u.work_status = $work_status, 
                u.company = $company, 
                u.designation = $designation, 
                u.last_job = $last_job, 
                u.last_role = $last_role, 
                u.degree = $degree, 
                u.graduation_year = $graduation_year
            """

            parameters = {
                "user_id": user_id,
                "name": name,
                "email": email,
                "phone": phone,
                "user_intent": user_intent,
                "interest_area": interest_area,
                "work_status": work_status,
                "company": company,
                "designation": designation,
                "last_job": last_job,
                "last_role": last_role,
                "degree": degree,
                "graduation_year": graduation_year
            }

            neo4j_conn.query(query, parameters)

            dispatcher.utter_message(text="Your information has been saved successfully. Thank you!")
            return []

        except Exception as e:
            dispatcher.utter_message(text="There was an error saving your information. Please try again later.")
            wandb.log({"error": str(e)})
            return []

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message['text']
        context = "You are an AI assistant knowledgeable about Crio. The user asked an undefined question. Please generate a helpful response."
        prompt = f"{context}\nUser query: {user_message}"
        response = generate_response(prompt)
        dispatcher.utter_message(text=response)

        return []