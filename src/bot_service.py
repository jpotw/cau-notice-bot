import logging
import time
import telegram
from google.cloud import secretmanager
import os
from dataclasses import dataclass
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

"""
functions for interacting with the Telegram bot and handling secrets
"""

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.environ['PROJECT_ID']}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
    

@dataclass
class BotConfig:
    bot: telegram.Bot
    telegram_chat_id: str
    cau_website_url: str
    cau_api_url: str
    library_website_url: str
    library_api_url: str


# for local testing
def initialize_bot_local() -> BotConfig:
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    bot = telegram.Bot(token=bot_token)
    
    return BotConfig(
        bot=bot,
        telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID'),
        cau_website_url=os.getenv('CAU_WEBSITE_URL'),
        cau_api_url=os.getenv('CAU_API_URL'),
        library_website_url=os.getenv('CAU_LIBRARY_WEBSITE_URL'),
        library_api_url=os.getenv('CAU_LIBRARY_API_URL')
    )


# for production (GCP)
def initialize_bot() -> BotConfig:
    bot_token = get_secret('TELEGRAM_BOT_TOKEN')
    bot = telegram.Bot(token=bot_token)
    
    return BotConfig(
        bot=bot,
        telegram_chat_id=get_secret('TELEGRAM_CHAT_ID'),
        cau_website_url=get_secret('CAU_WEBSITE_URL'),
        cau_api_url=get_secret('CAU_API_URL'),
        library_website_url=get_secret('CAU_LIBRARY_WEBSITE_URL'),
        library_api_url=get_secret('CAU_LIBRARY_API_URL')
    )


async def send_message_to_telegram(bot, chat_id, text):
    """텔레그램으로 메시지 전송"""
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode='HTML'
    )


async def send_notices_message(config, all_notices: List[Dict]):
    """텔레그램으로 공지사항 메시지 전송"""
    if all_notices:
        message = "<b>📢 새로운 공지사항이 있습니다.</b>\n\n"
        for notice in all_notices:
            message += (
                f"<b>[{notice['category']}]</b> "
                f"<b>{notice['title']}</b>\n"
                f"날짜: {notice['post_date']}\n"
            )
            if notice.get('url'):
                message += f"링크: <a href='{notice['url']}'>바로가기</a>\n"
            message += "\n"
                
        await config.bot.send_message(
            chat_id=config.telegram_chat_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True,
        )
