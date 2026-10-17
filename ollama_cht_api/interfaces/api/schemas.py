from pydantic import BaseModel, ConfigDict, Field


class WebhookMessageIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sender: str = Field(alias="from")
    message: str


class WebhookMessageOut(BaseModel):
    reply: str
