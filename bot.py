from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
import configparser
import logging
import random

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

STAFF_USER_IDS = []
STAFF_USER_IDS = [123456789, 987654321]
ADMIN_USER_IDS = [244268154]


class MenuItem:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} - ${self.price:.2f}"

class Order:
    def __init__(self, items: list, orderer_id: int):
        self.items = items
        self.orderer_id = orderer_id
        self.total_price = sum(item.price for item in items)

    def __str__(self):
        return "\n".join([str(item) for item in self.items])

# Define user roles and menu items
GENERAL_MENU = {
    1: MenuItem("Burger 🍔", 5.99),
    2: MenuItem("Pizza 🍕", 8.99),
    3: MenuItem("Pasta 🍝", 7.49),
    4: MenuItem("Salad 🥗", 4.99),
    5: MenuItem("Soda 🥤", 1.99),
    6: MenuItem("Hotdog 🌭", 3.49),
    7: MenuItem("Fries 🍟", 2.99)
}




# Dynamic menus (can be updated by staff)
todays_menu = {

}



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
        [KeyboardButton("Change General Menu")],
        [KeyboardButton("Set Today's Menu")],
        [KeyboardButton("View Orders")]
    ]
    keyboard_admin = [
        [KeyboardButton("Show Menu")],
        [KeyboardButton("Place Order")],
        [KeyboardButton("Change General Menu")],
        [KeyboardButton("Set Today's Menu")],
        [KeyboardButton("View Orders")]
    ]
    if user_id in ADMIN_USER_IDS:
        reply_markup = ReplyKeyboardMarkup(keyboard_admin, resize_keyboard=True)
    elif user_id in STAFF_USER_IDS:
        reply_markup = ReplyKeyboardMarkup(keyboard_staff, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardMarkup(keyboard_customer, resize_keyboard=True)
    
    # Send a message with the custom keyboard
    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

# Function to handle button clicks
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.message.from_user.id
       
    if user_id in ADMIN_USER_IDS:
        if text == "Show Menu":
            await show_menu(update, context)
        elif text == "Place Order":
            await show_order_menu(update, context)
        elif text ==  "Set Today's Menu":
            await set_todays_menu(update, context)
        elif text ==  "Change General Menu":
            await change_general_menu(update, context)
        elif text ==  "View Orders":
            await view_orders(update, context)
        else:
            await update.message.reply_text("Invalid option. Please choose again.")
    elif user_id in STAFF_USER_IDS:
        if text ==  "Set Today's Menu":
            await set_todays_menu(update, context)
        elif text ==  "Change General Menu":
            await change_general_menu(update, context)
        elif text ==  "View Orders":
            await view_orders(update, context)
        else:
            await update.message.reply_text("Invalid option. Please choose again.")
    else:
        if text == "Show Menu":
            await show_menu(update, context)
        elif text == "Place Order":
            await show_order_menu(update, context)
        else:
            await update.message.reply_text("Invalid option. Please choose again.")
    
    
    


#  ____  _         __  __ 
# / ___|| |_ __ _ / _|/ _|
# \___ \| __/ _` | |_| |_ 
#  ___) | || (_| |  _|  _|
# |____/ \__\__,_|_| |_|  
                        



def generate_toggle_menu(menu: dict, selected_items: dict) -> InlineKeyboardMarkup:
    keyboard = []

    for item_id, item in menu.items():
        is_selected = selected_items.get(item_id, False)
        emoji = "✅" if is_selected else "⬜"
        button = InlineKeyboardButton(f"{emoji} {item.name}", callback_data=f"staff_{item_id}")
        keyboard.append([button])

    # Add a submit button
    keyboard.append([InlineKeyboardButton("✅ Submit Today's Menu", callback_data="staff_submit_menu")])

    return InlineKeyboardMarkup(keyboard)

async def set_todays_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["menu_selection"] = {}
    
    await update.message.reply_text("Select items for today's menu:", reply_markup=generate_toggle_menu(GENERAL_MENU, {}))



async def handle_menu_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "staff_submit_menu":
        selected = context.user_data.get("menu_selection", {})
        
        todays_menu = {
            item_id: item_name
            for item_id, item_name in context.bot_data.get("general_menu", {}).items()
            if selected.get(item_id)
        }
        

        context.bot_data["todays_menu"] = todays_menu

        await query.edit_message_text("✅ Today's menu has been set.")
        
        context.user_data["menu_selection"] = {}
        return

    item_id = int(data.replace("staff_", ""))
    selected = context.user_data.setdefault("menu_selection", {})
    selected[item_id] = not selected.get(item_id, False)

    general_menu = context.bot_data.get("general_menu", {})
    await query.edit_message_text(
        text="Select items for today's menu:",
        reply_markup=generate_toggle_menu(general_menu, selected)
    )




async def change_general_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠️ Feature coming soon: Change General Menu.")

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = "📜Orders\n"
    for i in range(len(context.bot_data["orders"])):
        menu_text += f"Order#{i}: total price: {context.bot_data["orders"][i].total_price}"
        for item in context.bot_data["orders"][i].items:
            menu_text += f"\n   {item.name} - ${item.price:.2f}"
    await update.message.reply_text(menu_text, parse_mode="Markdown")
    # await update.message.reply_text(context.bot_data["orders"])

#   ____          _                            
#  / ___|   _ ___| |_ ___  _ __ ___   ___ _ __ 
# | |  | | | / __| __/ _ \| '_ ` _ \ / _ \ '__|
# | |__| |_| \__ \ || (_) | | | | | |  __/ |   
#  \____\__,_|___/\__\___/|_| |_| |_|\___|_|   
                                            

# Function to display the menu (text format)
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.bot_data["todays_menu"] or context.bot_data["todays_menu"] == {}:
        await update.message.reply_text("❗ Today's menu is not set yet.")
        return

    menu_text = "📜 *Today's Menu*\n\n"
    for key, value in context.bot_data["todays_menu"].items():
        menu_text += f"{key}. {value}\n"
    await update.message.reply_text(menu_text, parse_mode="Markdown")

def generate_order_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE,selected_items={}):
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if selected_items.get(option, False) else '⬜'} {item.name}", callback_data=str(option))]
        for option, item in context.bot_data["todays_menu"].items()
    ]
    keyboard.append([InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")])
    return InlineKeyboardMarkup(keyboard)


# Function to show the menu items as buttons
async def show_order_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = generate_order_buttons(update,context)
    await update.message.reply_text("Select options:", reply_markup=keyboard)  # Missing await

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
    await query.edit_message_text(text="Select options:", reply_markup=generate_order_buttons(update, context, selected_items))



# Function to place an order
# async def place_order(update: Update, context: ContextTypes.DEFAULT_TYPE, item_name: str) -> None:
#     await update.message.reply_text(f"✅ You have ordered: {item_name}. Your order is being processed!")

# Function to handle order confirmation
async def confirm_order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirm the order and send the selected items to the user."""
    query = update.callback_query
    await query.answer()

    selected_items = context.user_data.get("selected_items", {})
    selected_menu_items = [context.bot_data["todays_menu"][item] for item, selected in selected_items.items() if selected]

    if not selected_menu_items:
        await query.edit_message_text("⚠️ You haven't selected any items.")
    else:
        order = Order(selected_menu_items, update.effective_user.id)
        context.bot_data["orders"].append(order)
        order_summary = "\n".join([item.name for item in order.items])
        await query.edit_message_text(f"🛒 You've selected:\n{order_summary}\nThe tottal amount is {order.total_price}\nThank you for your order! 🎉")

    # Clear selected items after confirming
    context.user_data["selected_items"] = {}




# Bot launcher
def launch_bot():
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Access bot token from config file
    token = config["bot"]["key"]
    
    application = Application.builder().token(token).build()
    application.bot_data["general_menu"] = GENERAL_MENU
    # Shuffle the menu items
    TEMPORARY_MENU  = GENERAL_MENU.copy()
    application.bot_data["todays_menu"] = TEMPORARY_MENU
    application.bot_data["orders"] = []

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    
    application.add_handler(CallbackQueryHandler(handle_menu_toggle, pattern="^staff_"))
    application.add_handler(CallbackQueryHandler(order_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))



    # Start polling for updates from Telegram
    application.run_polling()

if __name__ == "__main__":
    launch_bot()
