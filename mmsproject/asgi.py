import os
from django.core.asgi import get_asgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmsproject.settings')

# Define the ASGI application
application = get_asgi_application()