import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

django_asgi_app = get_asgi_application()

try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack

    application = ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            # WebSocket routing to be attached in apps.conversations.routing
            "websocket": AuthMiddlewareStack(URLRouter([])),
        }
    )
except ImportError:
    application = django_asgi_app
