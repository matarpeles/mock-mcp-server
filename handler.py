# Lambda handler for Zappa deployment
from mangum import Mangum
from src.main import create_app

# Create the ASGI app
app = create_app()

# Wrap with Mangum for Lambda compatibility
handler = Mangum(app, lifespan="off")
