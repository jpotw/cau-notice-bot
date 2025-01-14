import os
import logging
from datetime import date, datetime
import requests
import time
from google.cloud import secretmanager
from src.notice_check import check_notices
from src.bot_service import initialize_bot_local, initialize_bot, send_notices_message
from typing import Dict, Any

async def main_local(request: Any) -> Dict[str, Any]:
    """로컬 테스트용 엔드포인트"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        config = initialize_bot_local()  # 로컬 테스트용 설정
        cau_notices, library_notices = check_notices(config)
        all_notices = cau_notices + library_notices
        
        await send_notices_message(config, all_notices)
        
        return {
            'statusCode': 200,
            'body': f'처리 완료. 학교 공지사항 {len(cau_notices)}개, 도서관 공지사항 {len(library_notices)}개를 전송했습니다.'
        }
        
    except Exception as e:
        logging.error(f"실행 중 오류 발생: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'오류가 발생했습니다: {str(e)}'
        }


async def main_cron(request):
    """Cloud Functions/Scheduler에서 실행되는 메인 함수"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        config = initialize_bot()  # 프로덕션 설정
        cau_notices, library_notices = check_notices(config)
        all_notices = cau_notices + library_notices
        
        await send_notices_message(config, all_notices)
        
        return {
            'statusCode': 200,
            'body': f'공지사항 체크 완료: 학교 공지사항 {len(cau_notices)}개, 도서관 공지사항 {len(library_notices)}개',
            'notices': {
                'cau': cau_notices,
                'library': library_notices
            }
        }
        
    except Exception as e:
        logging.error(f"실행 중 오류 발생: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'오류가 발생했습니다: {str(e)}'
        }
