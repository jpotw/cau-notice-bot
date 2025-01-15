import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from src.notice_check import is_notice_in_time_range
from src.main import main_local

def create_mock_datetime(year, month, day, hour, minute):
    """Mock datetime object creation"""
    return datetime(year, month, day, hour, minute, tzinfo=timezone(timedelta(hours=9)))

def create_mock_notice(write_dt: str, subject: str = "테스트 공지") -> dict:
    """Mock notice data creation"""
    return {
        'WRITE_DT': write_dt,
        'SUBJECT': subject,
        'BBS_SEQ': '12345'
    }

def create_mock_library_notice(date_created: str, title: str = "도서관 테스트 공지") -> dict:
    """Mock library notice data creation"""
    return {
        'dateCreated': date_created,
        'title': title,
        'id': '12345'
    }

@pytest.mark.parametrize("current_time,notice_time,expected", [
    # 당일 오전 8시 정각 (범위 끝)
    ((2024, 3, 21, 8, 0), (2024, 3, 21, 7, 59), True),
    # 전날 오전 8시 정각 (범위 시작)
    ((2024, 3, 21, 8, 0), (2024, 3, 20, 8, 0), True),
    # 범위 밖 (전날 오전 7시 59분)
    ((2024, 3, 21, 8, 0), (2024, 3, 20, 7, 59), False),
    # 범위 밖 (당일 오전 8시 1분)
    ((2024, 3, 21, 8, 0), (2024, 3, 21, 8, 1), False),
    # 임의의 현재 시간 (오후 3시) 에서의 테스트
    ((2024, 3, 21, 15, 0), (2024, 3, 21, 7, 59), True),
    ((2024, 3, 21, 15, 0), (2024, 3, 20, 8, 1), True),
    ((2024, 3, 21, 15, 0), (2024, 3, 20, 7, 59), False),
])
def test_notice_time_range(current_time, notice_time, expected):
    """Notice time range check test"""
    with patch('src.notice_check.get_korea_datetime') as mock_now:
        mock_now.return_value = create_mock_datetime(*current_time)
        notice_datetime = create_mock_datetime(*notice_time)
        assert is_notice_in_time_range(notice_datetime) == expected


@pytest.mark.asyncio
async def test_main_with_mock_notices():
    """Notification Check Test by Mock API"""
    test_time = create_mock_datetime(2024, 3, 21, 15, 0)
    
    mock_cau_notices = {
        'data': {
            'list': [
                create_mock_notice('2024-03-21 07:59:59', '범위 내 CAU 공지 1'),
                create_mock_notice('2024-03-20 08:01:00', '범위 내 CAU 공지 2'),
                create_mock_notice('2024-03-20 07:59:59', '범위 밖 CAU 공지 1'),
                create_mock_notice('2024-03-21 08:00:01', '범위 밖 CAU 공지 2'),
            ]
        }
    }
    
    mock_library_notices = {
        'success': True,
        'data': {
            'list': [
                create_mock_library_notice('2024-03-21 07:59:59', '범위 내 도서관 공지 1'),
                create_mock_library_notice('2024-03-20 08:01:00', '범위 내 도서관 공지 2'),
                create_mock_library_notice('2024-03-20 07:59:59', '범위 밖 도서관 공지 1'),
                create_mock_library_notice('2024-03-21 08:00:01', '범위 밖 도서관 공지 2'),
            ]
        }
    }
    
    with patch('src.notice_check.get_korea_datetime') as mock_now, \
         patch('requests.get') as mock_get:
        mock_now.return_value = test_time
        
        mock_response_cau = MagicMock()
        mock_response_cau.json.return_value = mock_cau_notices
        
        mock_response_library = MagicMock()
        mock_response_library.json.return_value = mock_library_notices
        
        mock_get.side_effect = [mock_response_cau, mock_response_library]
        
        result = await main_local({})
        
        assert result['statusCode'] == 200
        assert '처리 완료' in result['body']
        assert '학교 공지사항 2개' in result['body']
        assert '도서관 공지사항 2개' in result['body']