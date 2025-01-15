import os
import pytest
from src.main import main_local
from dotenv import load_dotenv

load_dotenv()



@pytest.mark.asyncio
async def test_main_error_handling():
    original_url = os.getenv('CAU_API_URL')
    os.environ['CAU_API_URL'] = "invalid_url"
    
    try:
        result = await main_local({})
        
        assert result['statusCode'] == 500
        assert '오류가 발생했습니다' in result['body']
    finally:
        os.environ['CAU_API_URL'] = original_url