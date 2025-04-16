from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
import configparser
import logging

# Define user roles and menu items
STAFF_USER_IDS = [123456789, 987654321]
MENU = {
    1: "Burger 🍔",
    2: "Pizza 🍕",
    3: "Pasta 🍝",
    4: "Salad 🥗",
    5: "Soda 🥤"
}

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Command to start and show the keyboard
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    await update.message.reply_text(f'Hello {username}! Your user ID is {user_id}.')
    
    keyboard_customer = [
        [KeyboardButton("Show Menu")],
        [KeyboardButton("Place Order")],
    ]
    keyboard_staff = [
        [KeyboardButton("View Orders")],
    ]

    if user_id not in STAFF_USER_IDS:
        reply_markup = ReplyKeyboardMarkup(keyboard_customer, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardMarkup(keyboard_staff, resize_keyboard=True)
    
    # Send a message with the custom keyboard
    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

# Function to handle button clicks
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "Show Menu":
        await show_menu(update, context)
    elif text == "Place Order":
        await show_order_menu(update, context)
    elif text in MENU.values():
        await place_order(update, context, text)
    elif text == "Cancel Order":
        await start(update, context)

# Function to show the menu items as buttons
async def show_order_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = generate_keyboard()
    await update.message.reply_text("Select options:", reply_markup=keyboard)  # Missing await


# Function to place an order
async def place_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_name: str) -> None:
    await update.message.reply_text(f"✅ You have ordered: {item_name}. Your order is being processed!")

# Function to display the menu (text format)
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    menu_text = "📜 *Menu*\n\n"
    for key, value in MENU.items():
        menu_text += f"{key}. {value}\n"
    
    await update.message.reply_text(menu_text, parse_mode="Markdown")

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu selection."""
    query = update.callback_query
    await query.answer()

    selected_option = query.data

    # If the user clicks "Confirm Order", call confirm_order_handler
    if selected_option == "confirm_order":
        await confirm_order_handler(update, context)
        return

    # Convert callback_data to int and toggle selection
    selected_option = int(selected_option)
    selected_items = context.user_data.setdefault("selected_items", {})
    selected_items[selected_option] = not selected_items.get(selected_option, False)

    # Update message with new keyboard state
    await query.edit_message_text(text="Select options:", reply_markup=generate_keyboard(selected_items))



def generate_keyboard(selected_items={}):
    """Generate inline keyboard with checkboxes and a confirm order button."""
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if selected_items.get(option, False) else '⬜'} {name}", callback_data=str(option))]
        for option, name in MENU.items()
    ]

    # Add the "Confirm Order" button
    keyboard.append([InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")])

    return InlineKeyboardMarkup(keyboard)


# Function to handle order confirmation
async def confirm_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirm the order and send the selected items to the user."""
    query = update.callback_query
    await query.answer()

    selected_items = context.user_data.get("selected_items", {})
    selected_menu_items = [MENU[item] for item, selected in selected_items.items() if selected]

    if not selected_menu_items:
        await query.edit_message_text("⚠️ You haven't selected any items.")
    else:
        order_summary = "\n".join(selected_menu_items)
        await query.edit_message_text(f"🛒 You've selected:\n{order_summary}\n\nThank you for your order! 🎉")

    # Clear selected items after confirming
    context.user_data["selected_items"] = {}

# Bot launcher
def launch_bot():
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Access bot token from config file
    token = config["bot"]["key"]
    
    application = Application.builder().token(token).build()

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))
    application.add_handler(CallbackQueryHandler(order_handler))

    # Start polling for updates from Telegram
    application.run_polling()

if __name__ == "__main__":
    launch_bot()
