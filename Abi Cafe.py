from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Replace with your NEW secure bot token
BOT_TOKEN = "7961512087:AAFneG_e_irwukt3IcpFZQSNj2_OQQHF0QM"

# Sample menu data with descriptions and images
MENU = {
    "Starters": [
        {"name": "Spring Rolls", "price": 135, "description": "Crispy rolls stuffed with fresh veggies.", "image": "https://thewoksoflife.com/wp-content/uploads/2015/09/spring-rolls-3.jpg"},
        {"name": "Garlic Bread", "price": 130, "description": "Crunchy bread with garlic butter.", "image": "https://www.ambitiouskitchen.com/wp-content/uploads/2023/02/Garlic-Bread-4-594x594.jpg"},
    ],
    "Main Course": [
        {"name": "Grilled Chicken", "price": 220, "description": "Juicy chicken grilled to perfection.", "image": "https://www.allrecipes.com/thmb/2_NsCoaHuJuqNyf9JfNjjh2uQ2M=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/GrilledFiveSpiceChicken.4x3-3a9a8efdbf554c42825297b82186f7e6.jpg"},
        {"name": "Pasta Alfredo", "price": 195, "description": "Creamy Alfredo sauce with rich pasta.", "image": "https://anitalianinmykitchen.com/wp-content/uploads/2018/09/alfredo-1-of-1-683x1024.jpg"},
    ],
    "Drinks": [
        {"name": "Coke", "price": 45, "description": "Cold and refreshing cola drink.", "image": "https://akm-img-a-in.tosshub.com/sites/media2/indiatoday/images/stories/2015January/coke-story_650_011515021116.jpg"},
        {"name": "Orange Juice", "price": 59, "description": "Freshly squeezed orange juice.", "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Orangejuice.jpg/235px-Orangejuice.jpg"},
    ]
}

# Delivery time estimates
DELIVERY_TIMES = {
    "small_order": "🕒 Estimated delivery time: 15-20 mins",
    "medium_order": "🕒 Estimated delivery time: 30-40 mins",
    "large_order": "🕒 Estimated delivery time: 45-60 mins"
}

# Store user orders and details
USER_ORDERS = {}
USER_DETAILS = {}

# Build the main menu keyboard
def build_menu_keyboard():
    buttons = [[InlineKeyboardButton(category, callback_data=f"category_{category}")]
               for category in MENU]

    buttons.append([InlineKeyboardButton("📋 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

# Build item selection keyboard
def build_items_keyboard(category):
    buttons = [
        [InlineKeyboardButton(f"{item['name']} - Birr {item['price']}", callback_data=f"item_{item['name']}")]
        for item in MENU[category]
    ]
    
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data="back_to_menu"),
        InlineKeyboardButton("📋 Main Menu", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(buttons)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🍴 Welcome to the Abi Cafe! Browse our delicious menu below:",
        reply_markup=build_menu_keyboard()
    )

# Handle Menu Navigation
async def menu_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith("category_"):
        category = query.data.split("_")[1]
        await query.edit_message_text(
            f"🍽️ {category} Menu:\nChoose an item below:",
            reply_markup=build_items_keyboard(category)
        )

    elif query.data.startswith("item_"):
        item_name = query.data.split("_")[1]
        chat_id = query.message.chat_id

        for category in MENU:
            for item in MENU[category]:
                if item['name'] == item_name:
                    item_details = (
                        f"🍲 *{item['name']}*\n"
                        f"💬 {item['description']}\n"
                        f"💰 Price: Birr {item['price']}"
                    )
                    await query.message.reply_photo(photo=item['image'], caption=item_details)
                    
                    if chat_id not in USER_ORDERS:
                        USER_ORDERS[chat_id] = []
                    
                    USER_ORDERS[chat_id].append(item['name'])
                    await query.answer(f"✅ {item['name']} added to your cart!")

    elif query.data == "back_to_menu":
        await query.edit_message_text(
            "🍴 Browse our delicious menu below:",
            reply_markup=build_menu_keyboard()
        )

    elif query.data == "main_menu":
        await query.edit_message_text(
            "🏠 Welcome back to the Main Menu! Choose a category below:",
            reply_markup=build_menu_keyboard()
        )

# Show Cart
async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    cart_items = USER_ORDERS.get(chat_id, [])

    if not cart_items:
        await update.message.reply_text("🛒 Your cart is empty. Add some tasty dishes from the menu!")
        return

    cart_summary = "\n".join([f"✅ {item}" for item in cart_items])
    await update.message.reply_text(f"🛒 Your Cart:\n{cart_summary}")

# Checkout Command
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    cart_items = USER_ORDERS.get(chat_id, [])

    if not cart_items:
        await update.message.reply_text("🛒 Your cart is empty. Add some items first!")
        return

    total_price = sum([item['price'] for category in MENU for item in MENU[category] if item['name'] in cart_items])
    
    USER_DETAILS[chat_id] = {"total_price": total_price}
    
    await update.message.reply_text("📝 Please provide your **Name** to confirm your order.")

# Collect User Details
async def handle_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if "name" not in USER_DETAILS[chat_id]:
        USER_DETAILS[chat_id]["name"] = text
        await update.message.reply_text("📞 Now, please provide your **Phone Number**.")
        return

    if "phone" not in USER_DETAILS[chat_id]:
        USER_DETAILS[chat_id]["phone"] = text
        
        name = USER_DETAILS[chat_id]["name"]
        phone = USER_DETAILS[chat_id]["phone"]
        total_price = USER_DETAILS[chat_id]["total_price"]
        cart_items = USER_ORDERS.get(chat_id, [])
        cart_summary = "\n".join([f"✅ {item}" for item in cart_items])

        await update.message.reply_text(
            f"✅ **Order Confirmation**\n"
            f"👤 Name: {name}\n"
            f"📞 Phone: {phone}\n"
            f"🛒 Items:\n{cart_summary}\n"
            f"💰 Total: **Birr {total_price}**\n"
            f"🚚 Your order is on the way! Thank you for ordering with Abi Cafe. 🍔"
        )

        USER_ORDERS[chat_id] = []
        USER_DETAILS[chat_id] = {}

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cart", view_cart))
    app.add_handler(CommandHandler("checkout", checkout))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_details))

    app.add_handler(CallbackQueryHandler(menu_navigation))

    print("Bot is running...")

    app.run_polling()
