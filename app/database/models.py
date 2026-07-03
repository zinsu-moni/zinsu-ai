from sqlalchemy import Column, BigInteger, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

Base = declarative_base()


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    role = Column(SAEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
