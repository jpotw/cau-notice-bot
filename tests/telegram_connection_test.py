import os
import pytest
from dotenv import load_dotenv
from telegram.ext import Application
from google.auth import default

def setup_module():
    """Load environment variables before running tests"""
    load_dotenv()

def test_env_variables_exist():
    """Test if all required environment variables are present"""
    required_vars = [
        'PROJECT_ID',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    for var in required_vars:
        assert os.getenv(var) is not None, f"Environment variable {var} is not set"
        assert os.getenv(var) != "", f"Environment variable {var} is empty"


@pytest.mark.asyncio
async def test_telegram_connection():
    """Test Telegram bot connection"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"\nTesting with chat_id: {chat_id}")
    
    application = Application.builder().token(bot_token).build()
    try:
        bot_info = await application.bot.get_me()
        assert bot_info is not None, "Failed to get bot information"
        print(f"Bot username: @{bot_info.username}")
        
        test_message = "🚨 Telegram Connection Test 🚨\nIf you see this message, the bot is working correctly!"
        message = await application.bot.send_message(chat_id=chat_id, text=test_message)
        assert message.text == test_message, "Failed to send test message"
        print(f"Test message sent successfully!")
        
    except Exception as e:
        pytest.fail(f"Telegram connection test failed: {str(e)}")
    finally:
        if application.running:
            await application.stop()

def test_gcp_connection():
    """Test GCP credentials"""
    try:
        # Test GCP credentials
        credentials, project = default()
        assert credentials is not None, "Failed to get GCP credentials"
        assert project is not None, "Failed to get GCP project"
    except Exception as e:
        pytest.fail(f"GCP connection test failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__])
