import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import F, Router, Bot
from app.config import bad_words
from aiogram.types import ChatPermissions
import re
from collections import defaultdict
from datetime import datetime, timedelta

router_admin = Router()
router_user = Router()
router = Router()
state = False
user_messages = defaultdict(list)
MESSAGE_LIMIT = 5
TIME_LIMIT = timedelta(seconds=10)


@router.message()
async def handle_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    now = datetime.now()
    messages = user_messages[user_id]

    user_messages[user_id] = [msg_time for msg_time in messages if now - msg_time < TIME_LIMIT]

    if len(user_messages[user_id]) >= MESSAGE_LIMIT:
        await message.answer("Do not spam!")
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        state = True
        await message.answer(f"User {message.from_user.first_name} muted for 10s")
        await asyncio.sleep(10)
        if state == True:
                await bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_other_messages=True,
                        can_pin_messages=True,
                        can_invite_users=True,
                        can_change_info=True
                    )
                )
                state = False
                await message.answer(f"User {message.from_user.first_name} unmuted")
        return  

    user_messages[user_id].append(now)

    text = message.text.lower()
    words_in_message = text.split()
    for word in words_in_message:
        for bad_word in bad_words:
            pattern = rf"{bad_word}\w*"
            if re.search(pattern, word):
                await message.delete()
                return
            

@router_user.edited_message()
async def bad_words_edited(message: Message):
    text = message.text.lower()
    words_in_message = text.split()
    for word in words_in_message:
        for bad_word in bad_words:
            pattern = rf"{bad_word}\w*"
            if re.search(pattern, word):
                await message.delete()
                return


@router_admin.message(Command('mute'))
async def mute_cmd(message: Message, bot: Bot):
    global state
    if not message.reply_to_message:
        return await message.reply("User not found.")
    
    args = message.text.split()
    if len(args) < 2:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        state = True
        await message.reply(f"User {message.reply_to_message.from_user.first_name} muted")
    else:
        try:
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.reply_to_message.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            state = True
            await message.reply(f"User {message.reply_to_message.from_user.first_name} muted for {args[1]}s")
            await asyncio.sleep(int(args[1]))
            if state == True:
                await bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.reply_to_message.from_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_other_messages=True,
                        can_pin_messages=True,
                        can_invite_users=True,
                        can_change_info=True
                    )
                )
                state = False
                await message.reply(f"User {message.reply_to_message.from_user.first_name} unmuted")
        except Exception:
            await message.reply("Invalid arguments")

@router_admin.message(Command('unmute'))
async def unmute_cmd(message: Message, bot: Bot):
    global state
    if not message.reply_to_message:
        return await message.reply("User not found.")
    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=message.reply_to_message.from_user.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_other_messages=True,
            can_pin_messages=True,
            can_invite_users=True,
            can_change_info=True
        )
    )
    state = False
    await message.reply(f"User {message.reply_to_message.from_user.first_name} unmuted")

@router_admin.message(Command('ban'))
async def ban_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("User not found.")
    await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.reply(f"User {message.reply_to_message.from_user.first_name} banned")


@router_admin.message(Command('help_admin'))
async def cmd_help(message: Message):
    await message.reply("Commands for admins:\n-----------------\n\\mute or \\mute (time in seconds) - mute member as reply for message\n-----------------\n\\unmute - unmute member as reply for message\n-----------------\n\\ban - ban member as reply for message")


@router_user.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Welcome to ModGuard! 🎉\nI’m here to help keep your chat safe and clean. Customize my settings to fit your needs, and let’s start moderating together! \nType /help to see all available commands.")


@router_user.message(Command('id'))
async def cmd_id(message: Message):
    await message.answer(f'ID:{message.from_user.id}')

@router_user.message(Command('help'))
async def cmd_help(message: Message):
    await message.reply("Commands for users:\n-----------------\n\\start - show start message\n-----------------\n\\id - show your telegram id\n-----------------\nIf you admin use \n\\help_admin")