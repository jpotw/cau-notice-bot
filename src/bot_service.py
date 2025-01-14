import logging
import time
import telegram
from google.cloud import secretmanager
import os
from dataclasses import dataclass
from typing import Dict, Any

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
    chat_id: str
    cau_website_url: str
    cau_api_url: str
    library_api_url: str


def initialize_bot() -> BotConfig:
    bot_token = get_secret('TELEGRAM_BOT_TOKEN')
    bot = telegram.Bot(token=bot_token)
    
    return BotConfig(
        bot=bot,
        chat_id=get_secret('TELEGRAM_CHAT_ID'),
        cau_website_url=get_secret('CAU_WEBSITE_URL'),
        cau_api_url=get_secret('CAU_API_URL'),
        library_api_url=get_secret('CAU_LIBRARY_API_URL')
    )


def create_notice_feed(title: str, post_date: str, cau_website_url: str = None, category: str = None) -> str:
    if category == '도서관':
        feed = (f"📚 도서관 새로운 공지사항\n\n"
               f"[{category}]\n{title}\n\n"
               f"📅 게시일: {post_date}")
    else:
        feed = (f"📢 새로운 공지사항입니다.\n\n"
               f"{title}\n\n"
               f"📅 게시일: {post_date}")
        if cau_website_url:
            feed += f"\n\n🔗 링크: {cau_website_url}"
    
    logging.info(feed)
    return feed


def send_notice(bot: telegram.Bot, chat_id: str, title: str, post_date: str, 
                cau_website_url: str = None, category: str = None) -> None:
    feed = create_notice_feed(title, post_date, cau_website_url, category)
    
    bot.send_message(
        text=feed,
        chat_id=chat_id,
        disable_web_page_preview=True
    )
    time.sleep(1)
    logging.info(f"공지사항 전송 완료: {title}")
