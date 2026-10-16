from fastapi import APIRouter, Depends

from ....application.use_cases import SendMessageUseCase
from ....dependencies import get_send_message_use_case
from ..schemas import WebhookMessageIn, WebhookMessageOut

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/whatsapp", response_model=WebhookMessageOut)
async def receive_whatsapp_message(
    payload: WebhookMessageIn,
    use_case: SendMessageUseCase = Depends(get_send_message_use_case),
) -> WebhookMessageOut:
    reply = await use_case.execute(conversation_id=payload.sender, user_message=payload.message)
    return WebhookMessageOut(reply=reply)
