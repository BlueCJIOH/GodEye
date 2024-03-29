from aiogram import types
from aiogram.dispatcher.filters import Filter

from bot.misc.env import Env


class ConnFilter(Filter):
    def __init__(self, is_connected: bool) -> None:
        self.is_connected = False

    async def check(self, msg: types.Message) -> bool:
        if self.is_connected:
            await msg.bot.send_message(
                Env.CHAT_ID, text="Вы уже подключены к камере!", parse_mode="Markdown"
            )
            return False
        self.is_connected = True
        return self.is_connected
