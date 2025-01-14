import unittest
from unittest.mock import Mock, patch
from src.notice_check import (
    check_school_notices,
    check_library_notices
)
from dotenv import load_dotenv
import os

load_dotenv()

class CrawlingTest(unittest.TestCase):
    def setUp(self):
        self.bot = Mock()
        def print_message(**kwargs):
            message = kwargs['text']
            if '도서관' in message:
                title = message.split(']')[1].split('\n\n')[0].strip()
            else:
                title = message.split('\n\n')[1].strip()
            print(f"제목: {title}")
        self.bot.send_message = Mock(side_effect=print_message)
        
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.cau_website_url = os.getenv('CAU_WEBSITE_URL')
        self.cau_api_url = os.getenv('CAU_API_URL')
        self.library_website_url = os.getenv('CAU_LIBRARY_WEBSITE_URL')
        self.library_api_url = os.getenv('CAU_LIBRARY_API_URL')

    def test_school_notices(self):
        try:
            notices = check_school_notices(
                self.cau_website_url,
                self.cau_api_url
            )
            
            self.assertIsInstance(notices, list)
            if notices:
                self.assertTrue(all(isinstance(notice, dict) for notice in notices))
                required_fields = {'title', 'post_date', 'category', 'url'}
                for notice in notices:
                    self.assertTrue(all(field in notice for field in required_fields),
                                 f"필수 필드 누락: {required_fields - set(notice.keys())}")
            self.assertGreaterEqual(len(notices), 0)
            
        except Exception as e:
            self.fail(f"학교 공지사항 크롤링 실패: {str(e)}")

    def test_library_notices(self):
        try:
            notices = check_library_notices(
                self.library_website_url,
                self.library_api_url
            )
        
            self.assertIsInstance(notices, list)
            if notices:
                self.assertTrue(all(isinstance(notice, dict) for notice in notices))
                required_fields = {'title', 'post_date', 'category'}
                for notice in notices:
                    self.assertTrue(all(field in notice for field in required_fields),
                                 f"필수 필드 누락: {required_fields - set(notice.keys())}")
            self.assertGreaterEqual(len(notices), 0)
            
        except Exception as e:
            self.fail(f"도서관 공지사항 크롤링 실패: {str(e)}")

    def test_notice_format(self):
        load_dotenv()
        
        cau_website_url = os.getenv('CAU_WEBSITE_URL')
        cau_api_url = os.getenv('CAU_API_URL')
        library_api_url = os.getenv('CAU_LIBRARY_API_URL')
        library_website_url = os.getenv('CAU_LIBRARY_WEBSITE_URL')
        
        school_notices = check_school_notices(cau_website_url, cau_api_url)
        if school_notices:
            for notice in school_notices:
                assert isinstance(notice, dict)
                assert 'title' in notice
                assert 'post_date' in notice
                assert 'category' in notice
                assert 'url' in notice
                assert notice['category'] == '학교'
                assert isinstance(notice['title'], str)
                assert isinstance(notice['post_date'], str)
                assert isinstance(notice['url'], str)
                assert notice['url'].startswith(cau_website_url)
                assert 'MENU_ID=100' in notice['url']
                assert 'SITE_NO=2' in notice['url']
                assert 'BOARD_SEQ=4' in notice['url']
                assert 'BBS_SEQ=' in notice['url']
        
        library_notices = check_library_notices(library_website_url, library_api_url)
        if library_notices:
            for notice in library_notices:
                assert isinstance(notice, dict)
                assert 'title' in notice
                assert 'post_date' in notice
                assert 'category' in notice
                assert notice['category'] == '도서관'
                assert isinstance(notice['title'], str)
                assert isinstance(notice['post_date'], str)
                assert isinstance(notice['url'], str)
                assert notice['url'].startswith(library_website_url)
                assert 'id' in notice['url']

if __name__ == '__main__':
    unittest.main()
