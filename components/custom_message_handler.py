from typing import Any, Text, Dict, List
from rasa.nlu.components import Component
from rasa.shared.nlu.training_data.message import Message

class CustomMessageHandler(Component):
    def process(self, message: Message, **kwargs: Any) -> None:
        if not message.get("text"):
            message.set("text", "", add_to_output=True)

    def create(self, config: Dict[Text, Any], **kwargs: Any) -> 'CustomMessageHandler':
        return self