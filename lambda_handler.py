# Direct Lambda handler for ASGI app
from mangum import Mangum
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import create_app

# Create app once at cold start
_app = None

def get_app():
    global _app
    if _app is None:
        _app = create_app()
    return _app

# Lambda handler
def handler(event, context):
    app = get_app()
    asgi_handler = Mangum(app, lifespan="off")
    return asgi_handler(event, context)
