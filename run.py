import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from app.handlers import router, router_admin, router_user
from aiogram.types import ChatPermissions
import app.config
import re
from collections import defaultdict
from datetime import datetime, timedelta



load_dotenv()
TOKEN = getenv('TOKEN2')
ADMIN = int(getenv('ADMIN'))
bot = Bot(TOKEN)


router_user.message.filter(F.chat.type == "supergroup")
router.message.filter(F.chat.type == "supergroup")
router_admin.message.filter(F.chat.type == "supergroup",F.from_user.id == ADMIN)


async def main():
    dp = Dispatcher()
    dp.include_router(router_user)
    dp.include_router(router_admin)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
      asyncio.run(main())
    except KeyboardInterrupt:
       print('Bot off')
