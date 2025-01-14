import unittest
import requests
import json
from datetime import date, datetime

class CrawlingTest(unittest.TestCase):
    def setUp(self):
        self.school_api_url = "https://www.cau.ac.kr/ajax/FR_SVC/BBSViewList2.do"
        self.school_params = {
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
        self.school_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=100&CONTENTS_NO=1',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }

        self.library_api_url = "https://library.cau.ac.kr/pyxis-api/1/bulletin-boards/1/bulletins"
        self.library_params = {
            'nameOption': '',
            'isSeq': 'false',
            'onlyWriter': 'false',
            'max': 10
        }
        self.library_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def test_school_api(self):
        try:
            res = requests.get(
                self.school_api_url, 
                params=self.school_params, 
                headers=self.school_headers
            )
            
            print("\n=== 학교 공지사항 API 응답 ===")
            print(f"Status Code: {res.status_code}")
            print("\nResponse Headers:")
            print(json.dumps(dict(res.headers), indent=2))
            
            data = res.json()
            print("\nResponse Body (sample):")
            if data.get('data', {}).get('list'):
                print(json.dumps(data['data']['list'][:2], indent=2, ensure_ascii=False))
                print(f"총 {len(data['data']['list'])}개의 공지사항")
            else:
                print("공지사항이 없습니다")
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('list', data.get('data', {}))
            
        except Exception as e:
            self.fail(f"학교 API 요청 실패: {str(e)}")

    def test_library_api(self):
        try:
            res = requests.get(
                self.library_api_url, 
                params=self.library_params, 
                headers=self.library_headers
            )
            
            print("\n=== 도서관 공지사항 API 응답 ===")
            print(f"Status Code: {res.status_code}")
            print("\nResponse Headers:")
            print(json.dumps(dict(res.headers), indent=2))
            
            data = res.json()
            print("\nResponse Body (sample):")
            if data.get('success') and data.get('data', {}).get('list'):
                print(json.dumps(data['data']['list'][:2], indent=2, ensure_ascii=False))
                print(f"총 {data['data']['totalCount']}개의 공지사항")
            else:
                print("공지사항이 없습니다")
            
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data.get('success'))
            self.assertIn('list', data.get('data', {}))
            
        except Exception as e:
            self.fail(f"도서관 API 요청 실패: {str(e)}")

    def test_current_date_notices(self):
        today = date.today()
        
        try:
            school_res = requests.get(
                self.school_api_url, 
                params=self.school_params, 
                headers=self.school_headers
            )
            school_data = school_res.json()
            
            if school_data.get('data', {}).get('list'):
                current_notices = [
                    notice for notice in school_data['data']['list']
                    if datetime.strptime(notice['WRITE_DT'].split('.')[0], '%Y-%m-%d %H:%M:%S').date() == today
                ]
                print("\n=== 오늘의 학교 공지사항 ===")
                print(f"오늘 날짜: {today}")
                print(f"현재 공지사항 수: {len(current_notices)}")
                if current_notices:
                    print("\n공지사항 목록:")
                    for notice in current_notices:
                        print(f"- {notice['SUBJECT']} ({notice['WRITE_DT']})")
            
        except Exception as e:
            self.fail(f"학교 현재 공지사항 필터링 실패: {str(e)}")
            
        try:
            library_res = requests.get(
                self.library_api_url, 
                params=self.library_params, 
                headers=self.library_headers
            )
            library_data = library_res.json()
            
            if library_data.get('success') and library_data.get('data', {}).get('list'):
                current_notices = [
                    notice for notice in library_data['data']['list']
                    if datetime.strptime(notice['dateCreated'], '%Y-%m-%d %H:%M:%S').date() == today
                ]
                print("\n=== 오늘의 도서관 공지사항 ===")
                print(f"오늘 날짜: {today}")
                print(f"현재 공지사항 수: {len(current_notices)}")
                if current_notices:
                    print("\n공지사항 목록:")
                    for notice in current_notices:
                        print(f"- {notice['title']} ({notice['dateCreated']})")
            
        except Exception as e:
            self.fail(f"도서관 현재 공지사항 필터링 실패: {str(e)}")

if __name__ == '__main__':
    unittest.main()
