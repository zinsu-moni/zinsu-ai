from abc import ABC, abstractmethod
from typing import List, Dict, Any
import aiohttp
import logging

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    pass


class AIClientTimeoutError(AIClientError):
    pass


class AIClientAPIError(AIClientError):
    pass


class AIClientRateLimitError(AIClientError):
    pass


class BaseAIClient(ABC):
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        pass


class OpenRouterClient(BaseAIClient):
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "openai/gpt-4o-mini"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model
        self.timeout = aiohttp.ClientTimeout(total=60)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
            "X-Title": "Zinsu AI"
        }

        payload = {
            "model": self.model,
            "messages": messages
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(self.BASE_URL, headers=headers, json=payload) as response:
                    if response.status == 429:
                        raise AIClientRateLimitError("Rate limit exceeded")
                    elif response.status != 200:
                        text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {text}")
                        raise AIClientAPIError(f"API request failed with status {response.status}")

                    data = await response.json()
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    content = message.get("content", "")

                    if not content:
                        raise AIClientError("Empty response from AI")

                    return content

        except aiohttp.ClientTimeoutError:
            raise AIClientTimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise AIClientError(f"Network error: {str(e)}")
