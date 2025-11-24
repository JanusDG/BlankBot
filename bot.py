from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CallbackContext
import configparser
import logging
import random

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

STAFF_USER_IDS = []
STAFF_USER_IDS = [123456789, 987654321,1619735577]
ADMIN_USER_IDS = [244268154]


class MenuItem:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} - {self.price:.2f}грн"

class Order:
    def __init__(self, items: list, orderer_id: int):
        self.items = items
        self.orderer_id = orderer_id
        self.total_price = sum(item.price for item in items)

    def __str__(self):
        return "\n".join([str(item) for item in self.items])

# Define user roles and menu items
GENERAL_MENU = {
    1: MenuItem("Бургер 🍔", 5.99),
    2: MenuItem("Піца 🍕", 8.99),
    3: MenuItem("Паста 🍝", 7.49),
    4: MenuItem("Салат 🥗", 4.99),
    5: MenuItem("Газований напій 🥤", 1.99),
    6: MenuItem("Хот-дог 🌭", 3.49),
    7: MenuItem("Картопля фрі 🍟", 2.99)
}




# Dynamic menus (can be updated by staff)
todays_menu = {

}



# Command to start and show the keyboard
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    await update.message.reply_text(f'Привіт, {username}! Твій ID користувача: {user_id}.')

    keyboard_customer = [
        [KeyboardButton("Показати меню")],
        [KeyboardButton("Зробити замовлення")],
    ]
    keyboard_staff = [
        [KeyboardButton("Змінити загальне меню")],
        [KeyboardButton("Встановити меню на сьогодні")],
        [KeyboardButton("Переглянути замовлення")],
        [KeyboardButton("Очистити замовлення")]
    ]
    keyboard_admin = [
        [KeyboardButton("Показати меню")],
        [KeyboardButton("Зробити замовлення")],
        [KeyboardButton("Змінити загальне меню")],
        [KeyboardButton("Встановити меню на сьогодні")],
        [KeyboardButton("Переглянути замовлення")],
        [KeyboardButton("Очистити замовлення")]
    ]

    if user_id in ADMIN_USER_IDS:
        reply_markup = ReplyKeyboardMarkup(keyboard_admin, resize_keyboard=True)
    elif user_id in STAFF_USER_IDS:
        reply_markup = ReplyKeyboardMarkup(keyboard_staff, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardMarkup(keyboard_customer, resize_keyboard=True)
    
    # Send a message with the custom keyboard
    await update.message.reply_text('Ласкаво просимо! Будь ласка, оберіть опцію:', reply_markup=reply_markup)


# Function to handle button clicks
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.message.from_user.id
        
    if user_id in ADMIN_USER_IDS:
        if text == "Показати меню":
            await show_menu(update, context)
        elif text == "Зробити замовлення":
            await show_order_menu(update, context)
        elif text == "Встановити меню на сьогодні":
            await set_todays_menu(update, context)
        elif text == "Змінити загальне меню":
            await change_general_menu(update, context)
        elif text == "Переглянути замовлення":
            await view_orders(update, context)
        elif text == "Очистити замовлення":
            await clear_orders(update, context)
        else:
            await update.message.reply_text("Невірна опція. Будь ласка, спробуйте ще раз.")
    elif user_id in STAFF_USER_IDS:
        if text == "Встановити меню на сьогодні":
            await set_todays_menu(update, context)
        elif text == "Змінити загальне меню":
            await change_general_menu(update, context)
        elif text == "Переглянути замовлення":
            await view_orders(update, context)
        elif text == "Очистити замовлення":
            await clear_orders(update, context)
        else:
            await update.message.reply_text("Невірна опція. Будь ласка, спробуйте ще раз.")
    else:
        if text == "Показати меню":
            await show_menu(update, context)
        elif text == "Зробити замовлення":
            await show_order_menu(update, context)
        else:
            await update.message.reply_text("Невірна опція. Будь ласка, спробуйте ще раз.")

        
    
    


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

    # Додати кнопку підтвердження
    keyboard.append([InlineKeyboardButton("✅ Підтвердити меню на сьогодні", callback_data="staff_submit_menu")])

    return InlineKeyboardMarkup(keyboard)

async def set_todays_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["menu_selection"] = {}

    await update.message.reply_text("Оберіть позиції для сьогоднішнього меню:", reply_markup=generate_toggle_menu(GENERAL_MENU, {}))


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

        await query.edit_message_text("✅ Меню на сьогодні встановлено.")
        
        context.user_data["menu_selection"] = {}
        return

    item_id = int(data.replace("staff_", ""))
    selected = context.user_data.setdefault("menu_selection", {})
    selected[item_id] = not selected.get(item_id, False)

    general_menu = context.bot_data.get("general_menu", {})
    await query.edit_message_text(
        text="Оберіть позиції для сьогоднішнього меню:",
        reply_markup=generate_toggle_menu(general_menu, selected)
    )




async def change_general_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠️ Незабаром: можливість змінювати загальне меню.")

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_text = "📜 Замовлення\n"
    for i in range(len(context.bot_data["orders"])):
        menu_text += f"Замовлення №{i}: загальна сума: {context.bot_data['orders'][i].total_price:.2f}грн"
        for item in context.bot_data["orders"][i].items:
            menu_text += f"\n   {item.name} – {item.price:.2f}грн"
    await update.message.reply_text(menu_text, parse_mode="Markdown")
    # await update.message.reply_text(context.bot_data["orders"])


#   ____          _                            
#  / ___|   _ ___| |_ ___  _ __ ___   ___ _ __ 
# | |  | | | / __| __/ _ \| '_ ` _ \ / _ \ '__|
# | |__| |_| \__ \ || (_) | | | | | |  __/ |   
#  \____\__,_|___/\__\___/|_| |_| |_|\___|_|   
                                            
# Функція для відображення меню (у текстовому форматі)
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.bot_data["todays_menu"] or context.bot_data["todays_menu"] == {}:
        await update.message.reply_text("❗ Меню на сьогодні ще не встановлено.")
        return

    menu_text = "📜 *Меню на сьогодні*\n\n"
    for key, value in context.bot_data["todays_menu"].items():
        menu_text += f"{key}. {value}\n"
    await update.message.reply_text(menu_text, parse_mode="Markdown")

def generate_order_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_items={}):
    keyboard = [
        [InlineKeyboardButton(f"{'✅' if selected_items.get(option, False) else '⬜'} {item.name}", callback_data=str(option))]
        for option, item in context.bot_data["todays_menu"].items()
    ]
    keyboard.append([InlineKeyboardButton("✅ Підтвердити замовлення", callback_data="confirm_order")])
    return InlineKeyboardMarkup(keyboard)
# Функція для показу меню як кнопок
async def show_order_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data["todays_menu"] or context.bot_data["todays_menu"] == {}:
        await update.message.reply_text("❗ Меню на сьогодні ще не встановлено.")
        return
    if update.message.from_user.id in [order.orderer_id for order in context.bot_data["orders"]]:
        await update.message.reply_text("❗ Ви вже зробили замовлення.")
        return
    keyboard = generate_order_buttons(update, context)
    await update.message.reply_text("Оберіть позиції:", reply_markup=keyboard)

async def clear_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очистити всі замовлення."""
    context.bot_data["orders"] = []
    await update.message.reply_text("Усі замовлення було очищено.")

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробити вибір у меню."""
    query = update.callback_query
    await query.answer()

    selected_option = query.data

    # Якщо користувач натискає "Підтвердити замовлення", викликаємо confirm_order_handler
    if selected_option == "confirm_order":
        await confirm_order_handler(update, context)
        return

    # Перетворити callback_data на int і перемкнути вибір
    selected_option = int(selected_option)
    selected_items = context.user_data.setdefault("selected_items", {})
    selected_items[selected_option] = not selected_items.get(selected_option, False)

    # Оновити повідомлення з новим станом кнопок
    await query.edit_message_text(
        text="Оберіть позиції:",
        reply_markup=generate_order_buttons(update, context, selected_items)
    )


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
        await query.edit_message_text("⚠️ Ви не вибрали жодного пункту меню.")
    else:
        order = Order(selected_menu_items, update.effective_user.id)
        context.bot_data["orders"].append(order)
        order_summary = "\n".join([item.name for item in order.items])
        await query.edit_message_text(f"🛒 Ви вибрали:\n{order_summary}\nСума замовлення {order.total_price}\nДякую за ваше замовлення 🎉")

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
