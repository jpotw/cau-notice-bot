import unittest
from datetime import date, datetime

class DateFormatTest(unittest.TestCase):
    def test_date_format_conversion(self):
        today = date.today()
        
        school_dates = [
            "2025-01-14 10:35:58.0",
            "2025-01-14 10:35:58",
            "2025.01.14 10:35:58",
            "2025.1.14 10:35:58"
        ]
        
        print("\n=== 학교 공지사항 날짜 변환 테스트 ===")
        for test_date in school_dates:
            try:
                if '.' in test_date:
                    if test_date.count('.') > 1:
                        parts = test_date.split(' ')
                        date_part = parts[0].replace('.', '-')
                        test_date = f"{date_part} {parts[1]}"
                    else:
                        test_date = test_date.split('.')[0]
                
                converted = datetime.strptime(test_date, '%Y-%m-%d %H:%M:%S').date()
                print(f"{test_date} -> {converted}")
                self.assertIsInstance(converted, date)
            except ValueError as e:
                self.fail(f"날짜 변환 실패 ({test_date}): {str(e)}")
        
        library_dates = [
            "1월 1일",
            "12월 31일",
            " 9월 5일 ",
            "10월 15일"
        ]
        
        print("\n=== 도서관 공지사항 날짜 변환 테스트 ===")
        for test_date in library_dates:
            try:
                date_parts = test_date.strip().replace('월', '').replace('일', '').split()
                month = int(date_parts[0])
                day = int(date_parts[1])
                
                if not (1 <= month <= 12 and 1 <= day <= 31):
                    raise ValueError("Invalid month or day")
                
                converted = f"{today.year}.{month:02d}.{day:02d}"
                print(f"{test_date} -> {converted}")
                
                datetime.strptime(converted, '%Y.%m.%d')
            except (ValueError, IndexError) as e:
                self.fail(f"날짜 변환 실패 ({test_date}): {str(e)}")

if __name__ == '__main__':
    unittest.main()
