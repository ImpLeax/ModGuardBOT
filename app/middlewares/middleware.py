from aiogram import BaseMiddleware
from aiogram.types import Message, ChatPermissions
import time
from aiogram.exceptions import TelegramBadRequest
import asyncio

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 5, interval: int =10, mute_duration:int = 30):
        self.limit = limit
        self.interval = interval
        self.mute_duration = mute_duration
        self.users = {}
        super().__init__()

    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        current_time = time.time()


        if user_id not in self.users:
            self.users[user_id] = {'messages': [], 'muted_until': 0}
        
        user_data = self.users[user_id]

        user_data['messages'] = [msg_time for msg_time in user_data['messages'] if current_time - msg_time < self.interval]

        if len(user_data['messages']) >= self.limit:
            if current_time > user_data['muted_until']:
                user_data['muted_until'] = current_time + self.mute_duration

                try:

                    await event.bot.restrict_chat_member(
                        chat_id=event.chat.id,
                        user_id=event.from_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=int(user_data['muted_until'])
                    )
                    await event.answer(f"User {event.from_user.first_name} muted for 30 seconds for spamming")
                    await event.bot.send_sticker(event.chat.id, sticker='CAACAgIAAxkBAAEIDuRmzzZUftMRrCE8XoDGKzYIVkC-0wACOhsAAk_f6Em9vkgwGEooeTUE')

                    await self.unmute_after_delay(event.bot, event.chat.id, event.from_user.id)
                    
                except TelegramBadRequest:
                    print("TelegramBadRequest,can not restrict admin")
        else:
            user_data['messages'].append(current_time)
            return await handler(event, data)
        

    async def unmute_after_delay(self, bot, chat_id, user_id):
        await asyncio.sleep(self.mute_duration)

        try:
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
            )
        except TelegramBadRequest as e:
            print(f"[ERROR] TelegramBadRequest: {e}. Cannot unmute user {user_id}.")