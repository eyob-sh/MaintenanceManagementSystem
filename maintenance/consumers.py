import json
import psycopg2
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from asgiref.sync import sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        self.user = self.scope["user"]
        await self.accept()

        # Start PostgreSQL LISTEN in a background thread
        await self.setup_postgres_listener()

    async def disconnect(self, close_code):
        pass  # Cleanup if needed

    async def setup_postgres_listener(self):
        def listen():
            conn = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            cursor.execute(f"LISTEN user_notifications_{self.user.id};")

            while True:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    # Send notification via WebSocket
                    self.channel_layer.send(
                        self.channel_name,
                        {
                            "type": "send_notification",
                            "notification": notify.payload
                        }
                    )

        # Run in a thread (since psycopg2 is blocking)
        import threading
        thread = threading.Thread(target=listen)
        thread.daemon = True
        thread.start()

    async def send_notification(self, event):
        await self.send(text_data=event["notification"])