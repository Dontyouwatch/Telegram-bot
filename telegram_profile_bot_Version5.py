import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
import re
from datetime import datetime
import signal
import sys

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize logger
logger = logging.getLogger(__name__)

# Token will be imported from config.py created by GitHub Actions
from config import TOKEN

class TelegramBot:
    def __init__(self):
        self.application = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        await update.message.reply_text(
            'Hi! Send me a Telegram username (starting with @) and I\'ll fetch all their profile pictures!'
        )

    async def get_profile_pics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get all profile pictures of the mentioned username."""
        message_text = update.message.text
        
        # Find username mentions in the message
        usernames = re.findall(r'@[\w_]+', message_text)
        
        if not usernames:
            await update.message.reply_text(
                "Please mention a username starting with @ to fetch their profile pictures."
            )
            return

        for username in usernames:
            try:
                # Remove @ from username
                clean_username = username[1:]
                
                # Get chat member info to get user_id
                chat = await context.bot.get_chat(username)
                user_id = chat.id
                
                # Get user's profile photos
                photos = await context.bot.get_user_profile_photos(user_id)
                
                if photos.total_count == 0:
                    await update.message.reply_text(f"{username} doesn't have any profile pictures!")
                    continue

                # Send information about total photos
                await update.message.reply_text(
                    f"Fetching all {photos.total_count} profile picture(s) for {username}!"
                )
                
                # Send all profile pictures
                for i in range(photos.total_count):
                    try:
                        photo = photos.photos[i][-1]  # Get highest quality version
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=photo.file_id,
                            caption=f"{username}'s profile picture {i+1}/{photos.total_count}"
                        )
                    except Exception as e:
                        logger.error(f"Error sending photo {i+1}: {str(e)}")
                        continue
                
                # Send completion message
                await update.message.reply_text(
                    f"✅ Finished sending all profile pictures for {username}"
                )
                    
            except TelegramError as e:
                await update.message.reply_text(
                    f"Sorry, I couldn't fetch profile pictures for {username}. "
                    "The user might not exist or I don't have access to their profile."
                )
                logger.error(f"Error fetching photos for {username}: {str(e)}")

    def handle_sigterm(self, signum, frame):
        """Handle SIGTERM signal gracefully"""
        logger.info("Received SIGTERM signal. Shutting down...")
        if self.application:
            self.application.stop()
        sys.exit(0)

    def run(self):
        """Start the bot."""
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.handle_sigterm)
        signal.signal(signal.SIGINT, self.handle_sigterm)

        # Create the Application
        self.application = Application.builder().token(TOKEN).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_profile_pics))

        # Start the Bot
        logger.info(f"Bot started at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        self.application.run_polling()

if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()