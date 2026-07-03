from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from app.config.settings import get_settings
from app.database.session import AsyncSessionLocal
from app.database.repositories import ConversationRepository
from app.ai import OpenRouterClient, AIService, AIClientError, AIClientTimeoutError, AIClientRateLimitError
import logging

router = Router()
settings = get_settings()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "👋 Hello! I'm Zinsu AI, your personal assistant.\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show all available commands\n"
        "/chat - Start chatting (or just send a message directly!)\n"
        "/reset - Clear conversation history\n\n"
        "Just send me a message and I'll respond!"
    )
    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📋 Zinsu AI Commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/chat - Start a chat session (or just message directly)\n"
        "/reset - Clear your conversation history\n\n"
        "You don't need /chat to chat - just send any message!"
    )
    await message.answer(help_text)


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as db:
        repo = ConversationRepository(db)
        ai_client = OpenRouterClient(settings.OPENROUTER_API_KEY)
        ai_service = AIService(ai_client, repo)
        await ai_service.reset_conversation(user_id)
    await message.answer("Conversation cleared successfully.")


@router.message(Command("chat"))
async def cmd_chat(message: Message):
    await message.answer("I'm ready to chat! Just send me a message.")


@router.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_text = message.text

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    try:
        async with AsyncSessionLocal() as db:
            repo = ConversationRepository(db)
            ai_client = OpenRouterClient(settings.OPENROUTER_API_KEY)
            ai_service = AIService(ai_client, repo)
            response = await ai_service.chat(user_id, user_text)

        try:
            await message.answer(response, parse_mode="Markdown")
        except TelegramBadRequest:
            await message.answer(response)

    except AIClientTimeoutError:
        await message.answer("⏱️ Sorry, the request timed out. Please try again.")
    except AIClientRateLimitError:
        await message.answer("⚠️ Rate limit exceeded. Please try again later.")
    except AIClientError as e:
        logger.error(f"AI error: {e}")
        await message.answer("❌ Sorry, something went wrong. Please try again later.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await message.answer("❌ An unexpected error occurred. Please try again later.")
