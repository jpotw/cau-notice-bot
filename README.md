# CAU Notice Bot v.0.1.0
<p align="center">
  <img src="cau_notice_bot_logo.png" width="300">
</p>

중앙대학교 공지사항 알림 텔레그램 봇

## 기능

- 중앙대학교 공지사항, 학술정보원 공지사항에서 새로운 공지사항이 등록되면 텔레그램으로 알림 전송
- 웹 스크래핑 방식이 아닌 API 호출을 통한 데이터 수집
- Google Cloud Functions를 통한 서버리스 운영


## 기술 스택

- Python 3.9
- Google Cloud Functions
- Google Cloud Secret Manager
- Telegram Bot API


## src 폴더 구조

- main.py: 메인 함수
- bot_service.py: 텔레그램 봇 관련 함수
- notice_check.py: 공지사항(api) 확인 함수

## 배포 방법

1. GCP 프로젝트 설정
   ```bash
   # GCP CLI 로그인
   gcloud auth login

   # API 활성화
   gcloud services enable cloudfunctions.googleapis.com cloudscheduler.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com
   ```

2. Secret Manager에 환경변수 설정
   ```bash
   # 각 환경변수를 Secret Manager에 저장
   echo -n "YOUR_BOT_TOKEN" | gcloud secrets create TELEGRAM_BOT_TOKEN --data-file=-
   echo -n "YOUR_CHAT_ID" | gcloud secrets create TELEGRAM_CHAT_ID --data-file=-
   echo -n "https://www.cau.ac.kr/cms/FR_CON/BoardView.do" | gcloud secrets create CAU_WEBSITE_URL --data-file=-
   echo -n "https://www.cau.ac.kr/ajax/FR_SVC/BBSViewList2.do" | gcloud secrets create CAU_API_URL --data-file=-
   echo -n "https://library.cau.ac.kr/guide/bulletins/notice" | gcloud secrets create CAU_LIBRARY_WEBSITE_URL --data-file=-
   echo -n "https://library.cau.ac.kr/pyxis-api/1/bulletin-boards/1/bulletins" | gcloud secrets create CAU_LIBRARY_API_URL --data-file=-
   ```

3. Cloud Functions 배포
   ```bash
   gcloud functions deploy gcp_cron \
     --gen2 \
     --runtime python39 \
     --trigger-http \
     --entry-point gcp_cron \
     --source . \
     --memory 256MB \
     --timeout 60s \
     --min-instances 0 \
     --max-instances 1 \
     --region asia-northeast3 \
     --allow-unauthenticated
   ```

4. Cloud Scheduler 설정
   ```bash
   # 매일 오전 8시에 실행되도록 설정
   gcloud scheduler jobs create http check_notices \
     --schedule="0 8 * * *" \
     --uri="https://asia-northeast3-[PROJECT_ID].cloudfunctions.net/gcp_cron" \
     --http-method=POST \
     --time-zone="Asia/Seoul" \
     --location="asia-northeast3"
   ```

## 로컬 테스트

1. 환경변수 설정
   - `.env` 파일을 생성하고 필요한 환경변수 설정
   - `poetry install`로 의존성 설치

2. 테스트 실행
   ```bash
   poetry run pytest
   ```
