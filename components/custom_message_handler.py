import re
import socket
import os
import openai
import wandb
from typing import Any, Dict, List, Text
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from neo4j import GraphDatabase
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
from typing import Any, Dict, List, Text

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
OPENAI_API_KEY = "OPENAI_API_KEY"  # Replace with your actual OpenAI API key
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
            model="gpt-35-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant with knowledge about Crio."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        # Specific exception handling for OpenAI errors
        wandb.log({"error": str(e)})
        print(f"OpenAI API Error: {e}")
        return "I'm sorry, I couldn't process your request at the moment."
    except Exception as e:
        # General exception handling
        wandb.log({"error": str(e)})
        print(f"General Error: {e}")
        return "I'm sorry, I couldn't process your request at the moment."

def get_text_embedding(text):
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response['data'][0]['embedding']
    except openai.error.OpenAIError as e:
        # Specific exception handling for OpenAI errors
        wandb.log({"error": str(e)})
        print(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        # General exception handling
        wandb.log({"error": str(e)})
        print(f"General Error: {e}")
        return None

@DefaultV1Recipe.register(
    component_types=["message"], is_trainable=True
)
class CustomMessageHandler(GraphComponent):
    @staticmethod
    def required_components() -> List[Text]:
        return []

    def __init__(self, config: Dict[Text, Any]) -> None:
        self.config = config

    def train(self, training_data: TrainingData) -> Resource:
        # Placeholder training logic
        # Initialize any required resources, connections, or data structures
        for example in training_data.training_examples:
            text = example.get("text")
            if text:
                # Example operation: prefetch embeddings for the training examples
                self.enhance_neo4j_with_embeddings(text)

        # Returning a dummy resource for now
        return Resource("custom_message_handler_resource")

    def process(self, messages: List[Message], **kwargs: Any) -> List[Message]:
        for message in messages:
            # Enhance Neo4j with text embeddings
            self.enhance_neo4j_with_embeddings(message.get("text"))
            # Check if the message needs to be answered by GPT-3.5-turbo
            if self.should_use_gpt(message):
                response = self.get_gpt_response(message.get("text"))
                message.set("text", response)
        return messages

    def should_use_gpt(self, message: Message) -> bool:
        # Logic to determine if GPT-3.5-turbo should answer the question
        # This can be based on confidence levels, intent detection, etc.
        return True  # For simplicity, let's assume we always use GPT for now

    def get_gpt_response(self, text: Text) -> Text:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-35-turbo-1106",
                messages=[{"role": "user", "content": text}]
            )
            return response.choices[0].message['content'].strip()
        except openai.error.OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            return "I'm sorry, but I couldn't process your request."
        except Exception as e:
            print(f"General Error: {e}")
            return "I'm sorry, but I couldn't process your request."

    def enhance_neo4j_with_embeddings(self, text: Text) -> None:
        try:
            embedding = self.get_text_embedding(text)
            with neo4j_conn._driver.session() as session:
                session.run(
                    "CREATE (n:Text {text: $text, embedding: $embedding})",
                    text=text,
                    embedding=embedding
                )
        except Exception as e:
            print(f"Error enhancing Neo4j: {e}")

    def get_text_embedding(self, text: Text) -> List[float]:
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except openai.error.OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            return []
        except Exception as e:
            print(f"General Error: {e}")
            return []

    @classmethod
    def create(
        cls, config: Dict[Text, Any], model_storage: ModelStorage, resource: Resource, execution_context: ExecutionContext
    ) -> GraphComponent:
        return cls(config)