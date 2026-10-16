from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities import Conversation, Message, MessageRole
from ...domain.repositories import ConversationRepository
from .models import ConversationModel, MessageModel


class PostgresConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        result = await self._session.execute(
            select(ConversationModel).where(ConversationModel.id == conversation_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        return Conversation(
            id=row.id,
            messages=[
                Message(role=MessageRole(m.role), content=m.content, created_at=m.created_at)
                for m in row.messages
            ],
        )

    async def save(self, conversation: Conversation) -> None:
        row = await self._session.get(ConversationModel, conversation.id)
        if row is None:
            row = ConversationModel(id=conversation.id)
            self._session.add(row)

        new_messages = conversation.messages[len(row.messages):]
        for message in new_messages:
            row.messages.append(
                MessageModel(role=message.role.value, content=message.content, created_at=message.created_at)
            )

        await self._session.commit()
