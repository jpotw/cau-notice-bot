import unittest
from unittest.mock import patch, MagicMock
from datetime import date
from src.main import check_notices, crawl_school_notices, crawl_library_notices

class TestCheckNotices(unittest.TestCase):
    def setUp(self):
        self.test_config = (
            MagicMock(),
            "test-chat-id",
            "https://www.cau.ac.kr/test",
            "https://library.cau.ac.kr/test", 
            "https://www.cau.ac.kr/api/test",
            "https://library.cau.ac.kr/api/test"
        )

    def test_successful_notice_check(self):
        with patch('src.crawl.initialize_bot', return_value=self.test_config), \
             patch('src.crawl.crawl_school_notices', return_value=1), \
             patch('src.crawl.crawl_library_notices', return_value=1):
            result = check_notices({})
            self.assertEqual(result['statusCode'], 200)
            self.assertIn("1개", result['body'])

    def test_error_handling(self):
        with patch('src.crawl.initialize_bot', side_effect=Exception("테스트 오류")):
            result = check_notices({})
            self.assertEqual(result['statusCode'], 500)
            self.assertIn("테스트 오류", result['body'])

    def test_crawling_with_no_new_notices(self):
        with patch('src.crawl.initialize_bot', return_value=self.test_config), \
             patch('src.crawl.crawl_school_notices', return_value=0), \
             patch('src.crawl.crawl_library_notices', return_value=0):
            result = check_notices({})
            self.assertEqual(result['statusCode'], 200)
            self.assertIn("0개", result['body'])

if __name__ == '__main__':
    unittest.main()
    