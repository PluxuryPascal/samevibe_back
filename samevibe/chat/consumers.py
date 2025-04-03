from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Chats, Contents


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        attachment = data.get("attachment")
        sender_lazy = self.scope["user"]

        await self.save_message(self.chat_id, sender_lazy, message, attachment)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender_lazy.username,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        await self.send(text_data=json.dumps({"message": message, "sender": sender}))

    @database_sync_to_async
    def save_message(self, chat_id, sender_lazy, message, attachment):
        User = get_user_model()
        sender = User.objects.get(pk=sender_lazy.pk)
        chat = Chats.objects.get(pk=chat_id)
        return Contents.objects.create(
            chat=chat, sender=sender, text=message, attachment=attachment
        )


class ChatListConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = f"chat_list_updates_{self.scope['user'].id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_update(self, event):
        data = event["data"]

        await self.send(text_data=json.dumps(data))
