#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bot as bot_module


class FakeMessage:
    def __init__(self):
        self.edits = []

    async def edit_message_text(self, text, **kwargs):
        self.edits.append(text)
        print(text)

    async def reply_text(self, text, **kwargs):
        self.edits.append(text)
        print(text)


class FakeCallbackQuery:
    def __init__(self, data):
        self.data = data
        self.message = FakeMessage()

    async def answer(self, *args, **kwargs):
        return None

    async def edit_message_text(self, text, **kwargs):
        await self.message.edit_message_text(text, **kwargs)


class FakeUpdate:
    def __init__(self, data):
        self.callback_query = FakeCallbackQuery(data)
        self.effective_chat = type('Chat', (), {'id': 1448843666})()
        self.message = None


class FakeContext:
    pass


class FakeBot:
    async def get_live_accounts(self):
        return [
            {'username': 'alpha', 'is_live': False, 'last_checked': None},
            {'username': 'beta', 'is_live': True, 'last_checked': None},
        ]


async def main():
    original_bot = bot_module.bot
    bot_module.bot = FakeBot()
    try:
        await bot_module.button_callback(FakeUpdate('help'), FakeContext())
        await bot_module.button_callback(FakeUpdate('status'), FakeContext())
        print('PASS: menu button callbacks responded')
    finally:
        bot_module.bot = original_bot


if __name__ == '__main__':
    asyncio.run(main())
