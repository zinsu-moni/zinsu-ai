from typing import List, Dict
from app.ai.client import BaseAIClient, AIClientError
from app.database.models import ConversationMessage, MessageRole
from app.database.repositories import ConversationRepository
import logging

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, ai_client: BaseAIClient, conversation_repo: ConversationRepository):
        self.ai_client = ai_client
        self.conversation_repo = conversation_repo

    async def chat(self, user_id: int, user_message: str) -> str:
        await self.conversation_repo.add_message(
            user_id=user_id,
            role=MessageRole.USER,
            content=user_message
        )

        history = await self.conversation_repo.get_conversation_history(user_id, limit=20)
        messages = self._format_messages(history)

        try:
            ai_response = await self.ai_client.chat(messages)
        except AIClientError as e:
            logger.error(f"AI client error: {e}")
            raise

        await self.conversation_repo.add_message(
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=ai_response
        )

        return ai_response

    async def reset_conversation(self, user_id: int) -> None:
        await self.conversation_repo.clear_conversation(user_id)

    def _format_messages(self, history: List[ConversationMessage]) -> List[Dict[str, str]]:
        messages = []
        for msg in history:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        return messages
