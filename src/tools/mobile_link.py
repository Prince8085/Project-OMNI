"""
Mobile Link Module for OMNI.
Connects to Telegram to allow remote control.
"""

import logging
import os
import asyncio
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class MobileLink:
    def __init__(self, callback: Callable[[str], str]):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.user_id = os.getenv("TELEGRAM_USER_ID", "") # For security
        self.callback = callback # Function to process command (brain.process_command)
        self.is_active = False
        
        if not self.token:
            logger.warning("Telegram Token not found. Mobile Link disabled.")
            return

        try:
            from telegram import Update
            from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
            
            self.app = ApplicationBuilder().token(self.token).build()
            
            # Handlers
            start_handler = CommandHandler('start', self.start)
            msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
            
            self.app.add_handler(start_handler)
            self.app.add_handler(msg_handler)
            
            self.is_active = True
            logger.info("Mobile Link initialized.")
            
        except ImportError:
            logger.warning("python-telegram-bot not installed. Mobile Link disabled.")
        except Exception as e:
            logger.error(f"Mobile Link init error: {e}")

    async def start(self, update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="OMNI Mobile Link Online.")

    async def handle_message(self, update, context):
        user_id = str(update.effective_user.id)
        if self.user_id and user_id != self.user_id:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Access Denied.")
            return

        text = update.message.text
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Processing...")
        
        # Process via Brain (Callback)
        # Note: This is blocking if brain is synchronous. Ideally brain should be async or run in thread.
        # For now, we assume callback handles threading or returns quickly.
        response = self.callback(text)
        
        # Extract speech or display
        reply = response.get('output', 'Done.')
        if isinstance(reply, str) and len(reply) > 4000:
            reply = reply[:4000] + "..."
            
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

    def run(self):
        """Run the bot polling."""
        if self.is_active:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.app.run_polling()
