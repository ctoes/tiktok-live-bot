#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bot as bot_module


class FakeMessage:
    def __init__(self):
        self.message_id = 123
        self.replies = []

    async def reply_text(self, text, **kwargs):
        self.replies.append(('reply_text', text))
        print(text)
        return self

    async def edit_text(self, text, **kwargs):
        self.replies.append(('edit_text', text))
        print(text)
        return self


class FakeChat:
    def __init__(self, chat_id):
        self.id = chat_id


class FakeUpdate:
    def __init__(self, chat_id):
        self.effective_chat = FakeChat(chat_id)
        self.message = FakeMessage()


class FakeApplication:
    def create_task(self, coro):
        return asyncio.create_task(coro)


class FakeContext:
    def __init__(self, args=None):
        self.args = args or []
        self.application = FakeApplication()


class FakeBotLogic:
    def __init__(self):
        class Monitor:
            async def check_live_status(self, username):
                return {
                    'username': username,
                    'is_live': True,
                    'timestamp': '2026-05-22T00:00:00',
                    'stream_info': {'title': 'Fake Live', 'viewers': 1},
                }

        self.monitor = Monitor()

    def start_recording_process(self, username, chat_id):
        process = type('P', (), {'wait': lambda self: None, 'poll': lambda self: 0, 'terminate': lambda self: None})()
        bot_module.active_recordings[chat_id] = {
            'username': username,
            'process': process,
            'stop_flag': False,
            'filepath': None,
            'output_path': os.path.join('downloads', f'{username}_fake.mp4'),
            'log_path': None,
            'log_file': None,
            'task': None,
        }
        return process

    def stop_recording_process(self, chat_id):
        session = bot_module.active_recordings.get(chat_id)
        if session:
            session['stop_flag'] = True
            return True
        return False


async def main():
    original_bot = bot_module.bot
    original_monitor = bot_module.monitor_recording_session
    bot_module.bot = FakeBotLogic()

    async def noop_monitor(*args, **kwargs):
        return None

    bot_module.monitor_recording_session = noop_monitor

    try:
        chat_id = 1448843666
        update = FakeUpdate(chat_id)
        context = FakeContext(args=['frank.the.fonk'])

        await bot_module.download_live_command(update, context)
        assert chat_id in bot_module.active_recordings, 'recording session not created'
        assert bot_module.active_recordings[chat_id]['username'] == 'frank.the.fonk'

        await bot_module.stop_download_command(update, context)
        assert bot_module.active_recordings[chat_id]['stop_flag'] is True, 'stop flag not set'

        print('PASS: rec/stop commands update active_recordings correctly')
    finally:
        bot_module.bot = original_bot
        bot_module.monitor_recording_session = original_monitor
        bot_module.active_recordings.clear()


if __name__ == '__main__':
    asyncio.run(main())
