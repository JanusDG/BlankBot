from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
import configparser
import logging

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Command to start and show the keyboard
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    await update.message.reply_text(f'Привіт {username}! Твій код користувача -  {user_id}.')
    

# Bot launcher
def launch_bot():
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Access bot token from config file
    token = config["bot"]["key"]
    
    application = Application.builder().token(token).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))

    # Start polling for updates from Telegram
    application.run_polling()

if __name__ == "__main__":
    launch_bot()
