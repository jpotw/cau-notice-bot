import os
import logging
from datetime import date, datetime
import requests
import time
from google.cloud import secretmanager
from src.notice_check import check_school_notices, check_library_notices
from bot_service import initialize_bot, send_notice
from typing import Dict, Any

"""
orchestrates the main logic of the application
"""

def main(request: Any) -> Dict[str, Any]:
    logging.basicConfig(level=logging.INFO)
    
    try:
        config = initialize_bot()
        school_notices = check_school_notices(
            config.cau_website_url, 
            config.cau_api_url
        )
        library_notices = check_library_notices(
            config.library_website_url,
            config.library_api_url
        )
        
        all_notices = school_notices + library_notices
        for notice in all_notices:
            send_notice(config.bot, config.chat_id, **notice)
        
        return {
            'statusCode': 200,
            'body': f'처리 완료. 학교 공지사항 {len(school_notices)}개, 도서관 공지사항 {len(library_notices)}개를 전송했습니다.'
        }
        
    except Exception as e:
        logging.error(f"실행 중 오류 발생: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'오류가 발생했습니다: {str(e)}'
        }
