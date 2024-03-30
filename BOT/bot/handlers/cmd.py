import asyncio
import json
import logging

import aiohttp
import websockets
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.utils.exceptions import RetryAfter

from bot.misc.env import Env
from bot.misc.filters import ConnFilter
from bot.states.states import EmployeeStatesGroup


async def start_monitoring(msg: Message) -> None:
    try:
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
                        await msg.bot.send_message(
                            Env.CHAT_ID,
                            text="Вы успешно подключились к камере! Теперь Вы можете отслеживать новые посещения.",
                            parse_mode="Markdown",
                        )
                        logging.info("Bot has successfully connected to the websocket.")
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
                                try:
                                    await msg.bot.send_message(
                                        Env.CHAT_ID, text=message, parse_mode="Markdown"
                                    )
                                except RetryAfter as e:
                                    await asyncio.sleep(e.timeout)
                                await asyncio.sleep(0.001)
                        else:
                            return
                    except Exception as e:
                        logging.error(f"inside ws-conn: {e}")
    except Exception as e:
        logging.error(f"outside ws-conn: {e}")


async def start_creating_employee(msg: Message) -> None:
    try:
        await EmployeeStatesGroup.first()
        await msg.bot.send_message(
            chat_id=Env.CHAT_ID,
            text=f'Отправьте фотографию лица сотрудника и введите название, которое должно соответствовать формату — "Имя Фамилия".',
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(e)


async def add_employee(msg: Message, state: FSMContext) -> None:
    try:
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
                url = "http://web:8000/employee/"
                file = await msg.bot.get_file(msg.photo[0].file_id)
                if not msg.caption:
                    await msg.bot.send_message(
                        chat_id=Env.CHAT_ID,
                        text="Пожалуйста, отправьте фотографию заново и введите название во время ее отправки!",
                        parse_mode="Markdown",
                    )
                    return
                file_name = msg.caption
                await msg.bot.download_file_by_id(file.file_id, f"{file_name}.png")
                response = await session.post(
                    url,
                    headers={"Authorization": f"Bearer {access_token}"},
                    data={
                        "img": open(f"{file_name}.png", "rb"),
                        "name": file_name,
                    },
                )
                await state.finish()
                if response.status == 201:
                    await msg.bot.send_message(
                        chat_id=Env.CHAT_ID,
                        text=f"Новый сотрудник успешно добавлен! Пожалуйста, перезагрузите камеру!",
                        parse_mode="Markdown",
                    )
                else:
                    await msg.bot.send_message(
                        chat_id=Env.CHAT_ID,
                        text=f"Отправьте фотографию заново и убедитесь в следующем:\n"
                        f"‼ фотография хорошего качества и содержит лицо человека;\n"
                        f'‼ надпись к фотографии — "Имя Фамилия"',
                        parse_mode="Markdown",
                    )
                    logging.error("Not valid photo!")
                    return
    except Exception as e:
        await state.finish()
        await msg.bot.send_message(
            chat_id=Env.CHAT_ID,
            text=f"Что-то пошло не так! Пожалуйста, попробуйте перезагрузить камеру или обратитесь в тех. поддержку!",
            parse_mode="Markdown",
        )
        logging.error(e)


async def delete_employee(msg: Message, state: FSMContext) -> None:
    try:
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
                url = f"http://web:8000/employee/{int(msg.text)}"
                response = await session.delete(
                    url, headers={"Authorization": f"Bearer {access_token}"}
                )
                if response.status == 204:
                    await state.finish()
                    await msg.bot.send_message(
                        chat_id=Env.CHAT_ID,
                        text="Сотрудник был успешно удален из базы данных!",
                        parse_mode="Markdown",
                    )
                    return
                await msg.bot.send_message(
                    chat_id=Env.CHAT_ID,
                    text="Не удалось удалить сотрудника, пожалуйста, проверьте корректность введенного кода и попробуйте заново!",
                    parse_mode="Markdown",
                )
    except Exception as e:
        await state.finish()
        await msg.bot.send_message(
            chat_id=Env.CHAT_ID,
            text=f"Что-то пошло не так! Пожалуйста, попробуйте перезагрузить камеру или обратитесь в тех. поддержку!",
            parse_mode="Markdown",
        )
        logging.error(e)


async def start_deleting_employee(msg: Message) -> None:
    try:
        await EmployeeStatesGroup.delete.set()
        await msg.bot.send_message(
            chat_id=Env.CHAT_ID,
            text=f"Отправьте код существующего сотрудника, чтобы удалить его из базы данных.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(e)


async def start_listing_employee(msg: Message) -> None:
    try:
        await EmployeeStatesGroup.list.set()
        await msg.bot.send_message(
            chat_id=Env.CHAT_ID,
            text=f"Отправьте номер страницы списка, чтобы увидеть существующих сотрудников.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(e)


async def list_employee(msg: Message, state: FSMContext) -> None:
    try:
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
                url = f"http://web:8000/employee/?page={int(msg.text)}"
                response = await session.get(
                    url, headers={"Authorization": f"Bearer {access_token}"}
                )
                if response.status == 200:
                    await state.finish()
                    content = await response.json()
                    text = ""
                    for el in content["results"]:
                        text += (
                            f"Код: {el['id']}\n"
                            f"Имя Фамилия: {el['first_name']} {el['last_name']}\n\n"
                        )
                    await msg.bot.send_message(
                        chat_id=Env.CHAT_ID,
                        text=text,
                        parse_mode="Markdown",
                    )
                    return
                await msg.bot.send_message(
                    chat_id=Env.CHAT_ID,
                    text="Не удалось получить список сотрудников, пожалуйста, проверьте корректность введенного номера страницы и попробуйте заново!",
                    parse_mode="Markdown",
                )
    except Exception as e:
        await state.finish()
        await msg.bot.send_message(
            chat_id=Env.CHAT_ID,
            text=f"Что-то пошло не так! Пожалуйста, попробуйте перезагрузить камеру или обратитесь в тех. поддержку!",
            parse_mode="Markdown",
        )
        logging.error(e)


def register_cmd_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_monitoring, ConnFilter(is_connected=False), commands="monitor"
    )
    dp.register_message_handler(start_creating_employee, commands="create", state=None)
    dp.register_message_handler(
        add_employee,
        state=EmployeeStatesGroup.img,
        content_types=[
            "photo",
        ],
    )
    dp.register_message_handler(start_deleting_employee, commands="delete", state=None)
    dp.register_message_handler(
        delete_employee,
        state=EmployeeStatesGroup.delete,
        content_types=[
            "text",
        ],
    )
    dp.register_message_handler(start_listing_employee, commands="list", state=None)
    dp.register_message_handler(
        list_employee,
        state=EmployeeStatesGroup.list,
        content_types=[
            "text",
        ],
    )
