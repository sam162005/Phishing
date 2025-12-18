from asgiref.wsgi import WsgiToAsgi
from app import app

# Wrap the Flask app with ASGI
app = WsgiToAsgi(app)
