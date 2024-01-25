"""
ASGI config for godeye project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from core.middleware import JWTAuthMiddleware
from log.api.v1.services.consumers import LogConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "godeye.settings")
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(
            URLRouter(
                [
                    re_path(r"ws/log/", LogConsumer.as_asgi()),
                ]
            )
        ),
    }
)
