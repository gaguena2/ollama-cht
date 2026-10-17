from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: MessageRole
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Conversation:
    id: str
    messages: list[Message] = field(default_factory=list)

    def add_message(self, role: MessageRole, content: str) -> Message:
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message

    def to_ollama_messages(self) -> list[dict]:
        return [{"role": m.role.value, "content": m.content} for m in self.messages]
