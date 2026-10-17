import httpx

from ..application.ports import ChatModelPort


class OllamaHttpClient(ChatModelPort):
    def __init__(self, base_url: str, model: str):
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
