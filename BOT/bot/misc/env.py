import logging
import os
from typing import Final


class Env:
    try:
        BOT_TOKEN: Final = os.environ["BOT_TOKEN"]
        CHAT_ID: Final = os.environ["CHAT_ID"]
        TG_NAME: Final = os.environ["TG_NAME"]
        TG_PWD: Final = os.environ["TG_PWD"]
    except KeyError as err:
        logging.warning(f"Set a valid {err} variable in the environment file!")
