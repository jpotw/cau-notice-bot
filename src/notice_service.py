from typing import List, Dict
import logging
from datetime import date, datetime
import requests


def check_school_notices(cau_notice_url: str, cau_api_url: str) -> List[Dict[str, str]]:
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
        'Referer': f'{cau_notice_url}',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }
    
    res = requests.get(cau_api_url, params=params, headers=headers)
    res.raise_for_status()
    
    data = res.json()
    today = date.today()
    
    notices = []
    for notice in data.get('data', {}).get('list', []):
        try:
            post_date = datetime.strptime(notice['WRITE_DT'].split('.')[0], '%Y-%m-%d %H:%M:%S').date()
            if today == post_date:
                notices.append({
                    'title': notice.get('SUBJECT', ''),
                    'post_date': notice['WRITE_DT'],
                    'category': '학교'
                })
        except Exception as e:
            logging.error(f"개별 공지사항 처리 중 오류 발생: {str(e)}")
            continue
    
    return notices

def check_library_notices(library_api_url: str) -> List[Dict[str, str]]:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        params = {
            'nameOption': '',
            'isSeq': 'false',
            'onlyWriter': 'false',
            'max': 10
        }

        res = requests.get(library_api_url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        today = date.today()
        
        notices = []
        if data.get('success') and data.get('data', {}).get('list'):
            for notice in data['data']['list']:
                try:
                    post_date = datetime.strptime(notice['dateCreated'], '%Y-%m-%d %H:%M:%S').date()
                    
                    if today == post_date:
                        notices.append({
                            'title': notice.get('title', ''),
                            'post_date': notice['dateCreated'],
                            'category': '도서관'
                        })
                
                except Exception as e:
                    logging.error(f"도서관 개별 공지사항 처리 중 오류 발생: {str(e)}")
                    continue
                    
        return notices
        
    except Exception as e:
        logging.error(f"도서관 공지사항 크롤링 중 오류 발생: {str(e)}")
        return []
