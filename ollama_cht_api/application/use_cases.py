from ..domain.entities import Conversation, MessageRole
from ..domain.repositories import ConversationRepository
from .ports import ChatModelPort


class SendMessageUseCase:
    def __init__(self, conversation_repository: ConversationRepository, chat_model: ChatModelPort):
        self._conversations = conversation_repository
        self._chat_model = chat_model

    async def execute(self, conversation_id: str, user_message: str) -> str:
        conversation = await self._conversations.get_by_id(conversation_id)
        if conversation is None:
            conversation = Conversation(id=conversation_id)

        conversation.add_message(MessageRole.USER, user_message)
        reply = await self._chat_model.chat(conversation.to_ollama_messages())
        conversation.add_message(MessageRole.ASSISTANT, reply)

        await self._conversations.save(conversation)
        return reply
