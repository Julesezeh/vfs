"""
Telegram notification handler for VFS bot
Sends alerts and updates via Telegram
"""

import logging
import html
from datetime import datetime
from typing import Optional
import asyncio
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """Handles Telegram notifications for the VFS booking bot"""

    def __init__(self, bot_token: str, chat_id: str, enabled: bool = True):
        """
        Initialize Telegram notifier

        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
            enabled: Whether notifications are enabled
        """
        self.enabled = enabled
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)

        if self.enabled:
            self.bot = Bot(token=bot_token)
        else:
            self.bot = None
            self.logger.info("Telegram notifications disabled")

    def _send_sync(self, message: str, photo_path: Optional[str] = None) -> bool:
        """
        Synchronous wrapper for sending messages

        Args:
            message: Message text to send
            photo_path: Optional path to photo to send with message

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                if photo_path:
                    loop.run_until_complete(
                        self.bot.send_photo(
                            chat_id=self.chat_id,
                            photo=open(photo_path, 'rb'),
                            caption=message
                        )
                    )
                else:
                    loop.run_until_complete(
                        self.bot.send_message(
                            chat_id=self.chat_id,
                            text=message,
                            parse_mode='HTML'
                        )
                    )
                return True
            finally:
                loop.close()

        except TelegramError as e:
            self.logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
            return False

    def send_message(self, message: str, photo_path: Optional[str] = None) -> bool:
        """
        Send a message via Telegram

        Args:
            message: Message text to send (may contain HTML tags)
            photo_path: Optional path to photo to send with message

        Returns:
            bool: True if sent successfully, False otherwise
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"🤖 <b>VFS Bot Update</b>\n⏰ {timestamp}\n\n{message}"

        self.logger.info(f"Sending Telegram notification: {message}")
        return self._send_sync(formatted_message, photo_path)

    def notify_start(self) -> bool:
        """Notify that bot has started"""
        return self.send_message("✅ VFS Booking Bot has started successfully!")

    def notify_slot_found(self, date: str, time: str, location: str, screenshot: Optional[str] = None) -> bool:
        """
        Notify that an appointment slot was found

        Args:
            date: Appointment date
            time: Appointment time
            location: Appointment location
            screenshot: Optional screenshot path
        """
        message = (
            f"🎉 <b>APPOINTMENT SLOT FOUND!</b>\n\n"
            f"📅 Date: {date}\n"
            f"⏰ Time: {time}\n"
            f"📍 Location: {location}\n\n"
            f"Check the bot for booking status!"
        )
        return self.send_message(message, screenshot)

    def notify_booking_success(self, appointment_details: dict, screenshot: Optional[str] = None) -> bool:
        """
        Notify successful booking

        Args:
            appointment_details: Dictionary with appointment details
            screenshot: Optional screenshot path
        """
        message = (
            f"✅ <b>BOOKING SUCCESSFUL!</b>\n\n"
            f"📅 Date: {appointment_details.get('date', 'N/A')}\n"
            f"⏰ Time: {appointment_details.get('time', 'N/A')}\n"
            f"📍 Location: {appointment_details.get('location', 'N/A')}\n"
            f"🎫 Reference: {appointment_details.get('reference', 'N/A')}\n\n"
            f"Check your email for confirmation!"
        )
        return self.send_message(message, screenshot)

    def notify_error(self, error_message: str, screenshot: Optional[str] = None) -> bool:
        """
        Notify about an error

        Args:
            error_message: Error description
            screenshot: Optional screenshot path
        """
        # Escape HTML entities to prevent Telegram parsing errors
        escaped_error = html.escape(str(error_message))
        message = f"❌ <b>ERROR OCCURRED</b>\n\n{escaped_error}"
        return self.send_message(message, screenshot)

    def notify_no_slots(self) -> bool:
        """Notify that no slots are available"""
        return self.send_message("ℹ️ No appointment slots available. Bot will keep checking...")

    def notify_retry(self, attempt: int, max_attempts: int, delay: int) -> bool:
        """
        Notify about retry attempt

        Args:
            attempt: Current attempt number
            max_attempts: Maximum attempts
            delay: Delay before retry in seconds
        """
        message = (
            f"🔄 Retrying operation...\n"
            f"Attempt {attempt}/{max_attempts}\n"
            f"Next attempt in {delay} seconds"
        )
        return self.send_message(message)

    def notify_custom(self, title: str, details: str, screenshot: Optional[str] = None) -> bool:
        """
        Send custom notification

        Args:
            title: Notification title
            details: Notification details
            screenshot: Optional screenshot path
        """
        message = f"<b>{title}</b>\n\n{details}"
        return self.send_message(message, screenshot)
