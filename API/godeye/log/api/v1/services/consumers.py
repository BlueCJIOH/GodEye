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
        if text_data_json["frame_date"] != "ping":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "log_message", "frame_date": text_data_json["frame_date"]},
            )

    async def log_message(self, event):
        logs = await self.get_logs(event["frame_date"])
        await self.send(
            json.dumps(
                {
                    "message": logs,
                }
            )
        )

    @database_sync_to_async
    def get_logs(self, frame_date) -> dict:
        return LogSerializer(
            Log.objects.filter(last_seen=frame_date),
            many=True,
        ).data
