import asyncio
import functions_framework
from src.main import main_cron
from flask import jsonify

@functions_framework.http
def gcp_cron(request):
    """Handles both CAU and library notices in a single function"""
    try:
        result = asyncio.run(main_cron(request))
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }), 500 