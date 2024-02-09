import json
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiohttp
import websockets

from bot.misc.env import Env

bot = Bot(token=Env.BOT_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


async def on_start_up(dp: Dispatcher) -> None:
    logging.info("Bot launched successfully.")
    async with aiohttp.ClientSession() as session:
        url = "http://web:8000/auth/signin/"
        response = await session.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"username": Env.TG_NAME, "password": Env.TG_PWD}),
        )
        if response.status == 200:
            data = await response.json()
            access_token = data["access"]
            ws_url = f"ws://web:8000/ws/log/?access_token={access_token}"

            async with websockets.connect(ws_url, ping_interval=None) as websocket:
                try:
                    response = await websocket.recv()
                    if json.loads(response)["status"] == "connected":
                        while True:
                            response = await websocket.recv()
                            message = "*Новые посещения:*\n"
                            for el in json.loads(response)["message"]:
                                message += (
                                    f"Имя: {el['employee']}\n"
                                    f"Время: {el['last_seen']}\n"
                                    f"Статус: {el['status']}\n\n"
                                )
                            await bot.send_message(
                                Env.CHAT_ID, text=message, parse_mode="Markdown"
                            )
                    else:
                        return
                except Exception as e:
                    logging.error(e)


def start_bot() -> None:
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up)
