from abc import ABC, abstractmethod

from .entities import Conversation


class ConversationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, conversation_id: str) -> Conversation | None: ...

    @abstractmethod
    async def save(self, conversation: Conversation) -> None: ...
