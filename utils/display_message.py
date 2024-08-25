import os

import yaml

messages_yamlfile = os.path.join(os.path.dirname(__file__), "messages.yaml")


class MessageLoader:
    def __init__(self):
        self._messages = None

    def _load_messages(self):
        if self._messages is None:
            with open(messages_yamlfile, "r") as file:
                self._messages = yaml.safe_load(file)
        return self._messages

    def load_error_messages(self):
        return self._load_messages()["errors"]

    def load_success_messages(self):
        return self._load_messages()["success"]

    def load_warning_messages(self):
        return self._load_messages()["warnings"]
