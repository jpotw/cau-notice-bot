from typing import List, Dict
import logging
from datetime import date, datetime
import requests
from urllib.parse import urlencode
from typing import Tuple

"""
functions for checking notices from the CAU API
"""

def check_cau_notices(cau_website_url: str, cau_api_url: str) -> List[Dict[str, str]]:
    params = {
        'SITE_NO': '2',
        'BOARD_SEQ': '4'
    }
    
    res = requests.get(cau_api_url, params=params)
    res.raise_for_status()
    
    data = res.json()
    today = date.today()
    
    notices = []
    for notice in data.get('data', {}).get('list', []):
        try:
            post_date = datetime.strptime(notice['WRITE_DT'].split('.')[0], '%Y-%m-%d %H:%M:%S').date()
            if today == post_date:
                url_params = {
                    'MENU_ID': '100',
                    'CONTENTS_NO': '1',
                    'SITE_NO': '2',
                    'BOARD_SEQ': '4',
                    'BBS_SEQ': notice.get('BBS_SEQ', '')
                }
                notice_url = f"{cau_website_url}?{urlencode(url_params)}"
                display_date = datetime.strptime(notice['WRITE_DT'].split('.')[0], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                notices.append({
                    'title': notice.get('SUBJECT', ''),
                    'post_date': display_date,
                    'category': 'CAU 공지',
                    'url': notice_url
                })
        except Exception as e:
            logging.error(f"개별 공지사항 처리 중 오류 발생: {str(e)}")
            continue
    
    return notices

def check_library_notices(library_website_url: str, library_api_url: str) -> List[Dict[str, str]]:
    try:
        res = requests.get(library_api_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        today = date.today()
        
        notices = []
        if data.get('success') and data.get('data', {}).get('list'):
            for notice in data['data']['list']:
                try:
                    post_date = datetime.strptime(notice['dateCreated'], '%Y-%m-%d %H:%M:%S').date()
                    
                    if today == post_date:
                        display_date = datetime.strptime(notice['dateCreated'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                        notices.append({
                            'title': notice.get('title', ''),
                            'post_date': display_date,
                            'category': '학술정보원 공지',
                            'url': f"{library_website_url}/{notice['id']}"
                        })
                
                except Exception as e:
                    logging.error(f"도서관 개별 공지사항 처리 중 오류 발생: {str(e)}")
                    continue
                    
        return notices
        
    except Exception as e:
        logging.error(f"도서관 공지사항 크롤링 중 오류 발생: {str(e)}")
        return []


def check_notices(config) -> Tuple[List[Dict], List[Dict]]:
    """공지사항을 체크하고 반환하는 핵심 로직"""
    cau_notices = check_cau_notices(
        config.cau_website_url,
        config.cau_api_url
    )
    
    library_notices = check_library_notices(
        config.library_website_url,
        config.library_api_url
    )
    return cau_notices, library_notices