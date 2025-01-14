import os
import logging
from bs4 import BeautifulSoup
from datetime import date
import requests
import time
import telegram
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.environ['PROJECT_ID']}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def initialize_bot():
    TOKEN = get_secret('TELEGRAM_BOT_TOKEN')
    CHAT_ID = get_secret('TELEGRAM_CHAT_ID')
    CAU_NOTICE_URL = get_secret('CAU_NOTICE_URL')
    CAU_LIBRARY_NOTICE_URL = get_secret('CAU_LIBRARY_NOTICE_URL')
    CAU_API_URL = get_secret('CAU_API_URL')
    CAU_LIBRARY_API_URL = get_secret('CAU_LIBRARY_API_URL')
    
    bot = telegram.Bot(token=TOKEN)
    return bot, CHAT_ID, CAU_NOTICE_URL, CAU_LIBRARY_NOTICE_URL, CAU_API_URL, CAU_LIBRARY_API_URL


def send_notice(bot, chat_id, title, post_date, notice_url=None, category=None):
    if category:
        feed = (f"📚 도서관 새로운 공지사항\n\n"
               f"[{category}]\n{title}\n\n"
               f"📅 게시일: {post_date}")
    else:
        feed = (f"📢 새로운 공지사항입니다.\n\n"
               f"{title}\n\n"
               f"📅 게시일: {post_date}")
        if notice_url:
            feed += f"\n\n🔗 링크: {notice_url}"
    
    bot.send_message(
        text=feed,
        chat_id=chat_id,
        disable_web_page_preview=True
    )
    time.sleep(1)
    logging.info(f"공지사항 전송 완료: {title}")


def check_notices(request):
    logging.basicConfig(level=logging.INFO)
    
    try:
        bot, chat_id, cau_url, library_url, cau_api_url, library_api_url = initialize_bot()
        
        sent_count = crawl_school_notices(bot, chat_id, cau_url, cau_api_url)
        
        library_sent = crawl_library_notices(bot, chat_id, library_url, library_api_url)
        
        return {
            'statusCode': 200,
            'body': f'처리 완료. 학교 공지사항 {sent_count}개, 도서관 공지사항 {library_sent}개를 전송했습니다.'
        }
        
    except Exception as e:
        logging.error(f"실행 중 오류 발생: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'오류가 발생했습니다: {str(e)}'
        }

def crawl_school_notices(bot, chat_id, url, api_url):
    params = {
        'pageNo': '1',
        'MENU_ID': '100',
        'SITE_NO': '2',
        'BOARD_SEQ': '4',
        'P_TAB_NO': '',
        'TAB_NO': '',
        'S_CATE_SEQ': '',
        'S_KEY': '',
        'S_SUBJECT': ''
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': url,
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }
    
    res = requests.get(api_url, params=params, headers=headers)
    res.raise_for_status()
    
    data = res.json()
    today = date.today().strftime('%Y.%m.%d')
    sent_count = 0
    
    for notice in data.get('list', []):
        try:
            post_date = notice.get('WRITE_DATE', '').split(' ')[0]
            if today == post_date:
                title = notice.get('SUBJECT', '')
                notice_id = notice.get('BBS_SEQ', '')
                notice_url = f'{url}&BOARD_SEQ={notice_id}'
                
                send_notice(bot, chat_id, title, post_date, notice_url)
                sent_count += 1
        except Exception as e:
            logging.error(f"개별 공지사항 처리 중 오류 발생: {str(e)}")
            continue
    
    return sent_count

def crawl_library_notices(bot, chat_id, url, api_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        params = {
            'page': 1,
            'limit': 10
        }
        
        res = requests.get(api_url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        today = date.today().strftime('%Y-%m-%d')
        sent_count = 0
        
        for notice in data.get('data', []):
            try:
                post_date = notice.get('createdAt', '').split('T')[0]
                
                if today == post_date:
                    title = notice.get('title', '')
                    category = notice.get('category', {}).get('name', '일반')
                    
                    send_notice(bot, chat_id, title, post_date, category=category)
                    sent_count += 1
            
            except Exception as e:
                logging.error(f"도서관 개별 공지사항 처리 중 오류 발생: {str(e)}")
                continue
                
        return sent_count
        
    except Exception as e:
        logging.error(f"도서관 공지사항 크롤링 중 오류 발생: {str(e)}")
        return 0
