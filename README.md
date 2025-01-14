# CAU Notice Bot v.0.1.0

중앙대학교 공지사항 알림 텔레그램 봇

## 기능

- 중앙대학교 공지사항, 학술정보원 공지사항에서 새로운 공지사항이 등록되면 텔레그램으로 알림 전송 (오전 8시, 오후 3시 두 차례 확인)
- 웹 스크래핑 방식이 아닌 API 호출을 통한 데이터 수집
- Google Cloud Functions를 통한 서버리스 운영


## 기술 스택

- Python 3.9
- Google Cloud Functions
- Google Cloud Secret Manager
- Telegram Bot API
- BeautifulSoup4


## src 폴더 구조

- main.py: 메인 함수
- bot_service.py: 텔레그램 봇 관련 함수
- notice_check.py: 공지사항(api) 확인 함수

## 배포 방법

1. GCP Cloud Functions에 배포
   - `check_cau_notices` 함수 배포
   - `check_library_notices` 함수 배포
   - 각 함수의 런타임 환경변수에 `.env` 파일의 내용 설정

2. Cloud Scheduler 설정
   - CAU 공지사항, 학술정보원 공지사항: 매일 08:00에 실행 (크론: `0 8 * * *`)
