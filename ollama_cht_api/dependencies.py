from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .application.use_cases import SendMessageUseCase
from .config import Settings, get_settings
from .infrastructure.ollama_client import OllamaHttpClient
from .infrastructure.persistence.database import create_engine_and_session
from .infrastructure.persistence.repository import PostgresConversationRepository

settings = get_settings()
engine, session_factory = create_engine_and_session(settings.database_url)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


def get_ollama_client(settings: Settings = Depends(get_settings)) -> OllamaHttpClient:
    return OllamaHttpClient(base_url=settings.ollama_base_url, model=settings.ollama_model)


def get_send_message_use_case(
    session: AsyncSession = Depends(get_session),
    ollama_client: OllamaHttpClient = Depends(get_ollama_client),
) -> SendMessageUseCase:
    repository = PostgresConversationRepository(session)
    return SendMessageUseCase(conversation_repository=repository, chat_model=ollama_client)
