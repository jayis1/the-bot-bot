import logging
import asyncio
import discord

class DiscordLogHandler(logging.Handler):
    def __init__(self, bot, channel_id, level=logging.NOTSET):
        super().__init__(level)
        self.bot = bot
        self.channel_id = channel_id
        self.queue = asyncio.Queue()
        self.task = self.bot.loop.create_task(self._log_sender())

    async def _log_sender(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"ERROR: DiscordLogHandler: Channel with ID {self.channel_id} not found.")
            return

        while True:
            try:
                record = await self.queue.get()
                log_entry = self.format(record)
                if len(log_entry) > 1990:
                    log_entry = log_entry[:1990] + "..."
                await channel.send(f"```log\n{log_entry}\n```")
            except Exception as e:
                print(f"Error in DiscordLogHandler: {e}")

    def emit(self, record):
        self.queue.put_nowait(record)

    def close(self):
        self.task.cancel()
        super().close()
