# my_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f"notifications_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send_notifications()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notifications(self):
        notifications = await self.get_notifications()
        await self.send(text_data=json.dumps(notifications))

    @database_sync_to_async
    def get_notifications(self):
        notifications = Notification.objects.filter(user=self.user, is_read=False).order_by('-timestamp')[:10]
        return [
            {
                'id': notification.id,
                'type': notification.type,
                'message': notification.message,
                'timestamp': notification.timestamp.isoformat(),
                'url': notification.url,
            }
            for notification in notifications
        ]

    async def send_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps([notification])))