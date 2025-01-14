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
        self.cau_url = os.getenv('CAU_NOTICE_URL')
        self.library_url = os.getenv('CAU_LIBRARY_NOTICE_URL')
        self.cau_api_url = os.getenv('CAU_API_URL')
        self.library_api_url = os.getenv('CAU_LIBRARY_API_URL')

    def test_school_notices(self):
        try:
            notices = check_school_notices(
                self.cau_url,
                self.cau_api_url
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
            self.fail(f"학교 공지사항 크롤링 실패: {str(e)}")

    def test_library_notices(self):
        try:
            notices = check_library_notices(
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

if __name__ == '__main__':
    unittest.main()
