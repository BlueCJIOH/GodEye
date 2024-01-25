import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from log.api.v1.serializers.log import LogSerializer
from log.models import Log


class LogConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.data = None
        self.room_group_name = None

    async def connect(self):
        self.room_group_name = "log"
        if str(self.scope["user"]) == "AnonymousUser":
            await self.disconnect(code=401)
        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({"status": "connected"}))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "log_message", "date_from": text_data_json['date_from'], "date_to": text_data_json["date_to"]},
        )

    async def log_message(self, event):
        logs = await self.get_logs(event['date_from'], event['date_to'])
        await self.send(
            json.dumps(
                {
                    "message": logs,
                }
            )
        )

    @database_sync_to_async
    def get_logs(self, date_from, date_to) -> dict:
        return LogSerializer(
            Log.objects.filter(last_seen__range=(date_from, date_to)),
            many=True,
        ).data
