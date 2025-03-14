"""
ASGI config for MaintenanceManagementSystem project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MaintenanceManagementSystem.settings')

# application = get_asgi_application()


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from maintenance import consumers  # Import your WebSocket consumer from the appropriate app

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MaintenanceManagementSystem.settings')

# Define the ASGI application
application = ProtocolTypeRouter({
    # HTTP requests are handled by the default Django ASGI application
    "http": get_asgi_application(),

    # WebSocket requests are handled by the URLRouter
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Add your WebSocket routes here
            path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),
        ])
    ),
})