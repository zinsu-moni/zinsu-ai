from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database.models import ConversationMessage, MessageRole


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_message(
        self,
        user_id: int,
        role: MessageRole,
        content: str
    ) -> ConversationMessage:
        message = ConversationMessage(
            user_id=user_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_conversation_history(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[ConversationMessage]:
        stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.user_id == user_id)
            .order_by(ConversationMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def clear_conversation(self, user_id: int) -> None:
        stmt = delete(ConversationMessage).where(ConversationMessage.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.commit()
