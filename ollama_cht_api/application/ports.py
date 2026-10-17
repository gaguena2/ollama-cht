from abc import ABC, abstractmethod


class ChatModelPort(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str: ...
