from __future__ import annotations

import json
import os

import httpx


class OpenAIError(RuntimeError):
    pass


class OpenAITimeoutError(OpenAIError):
    pass


class CodexService:
    """
    Async wrapper around OpenAI Chat Completions API.

    Replaces the former Codex CLI subprocess approach so that the bot
    works inside Docker without needing a CLI binary.
    """

    BASE_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        *,
        model: str = "gpt-4.1-nano",
        timeout_seconds: int = 60,
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._timeout = timeout_seconds
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    async def chat(self, *, prompt: str) -> str:
        if not self._api_key:
            raise OpenAIError("OPENAI_API_KEY is not set")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                resp = await client.post(self.BASE_URL, headers=headers, json=payload)
            except httpx.TimeoutException as e:
                raise OpenAITimeoutError("OpenAI API timed out") from e

            if resp.status_code != 200:
                raise OpenAIError(f"OpenAI API error {resp.status_code}: {resp.text}")

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise OpenAIError("OpenAI returned no choices")

            return str(choices[0]["message"]["content"]).strip()
