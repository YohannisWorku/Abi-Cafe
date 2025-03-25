from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Replace with your NEW secure bot token
BOT_TOKEN = "7961512087:AAFneG_e_irwukt3IcpFZQSNj2_OQQHF0QM"
ADMIN_ID = 6472125371  # Replace with your Telegram ID
USER_LIST = set()  # Stores all active user chat IDs


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
# save data function
def save_data():
    data = {
        "USER_ORDERS": USER_ORDERS or {},
        "USER_DETAILS": USER_DETAILS or {}
    }
    

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
    chat_id = update.message.chat_id
    USER_LIST.add(chat_id)  # Track each user who starts the bot

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

    total_price = sum(
        [item['price'] for category in MENU for item in MENU[category] if item['name'] in cart_items]
    )

    # Ensure all required keys are initialized
    USER_DETAILS[chat_id] = {
        "name": None,
        "phone": None,
        "items": cart_items,
        "total_price": total_price
    }

    save_data()  # Save data after initializing USER_DETAILS
    await update.message.reply_text("📝 Please provide your **Name** to confirm your order.")



# Collect User Details
async def handle_user_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    # Ensure USER_DETAILS entry exists before modifying it
    if chat_id not in USER_DETAILS:
        USER_DETAILS[chat_id] = {"name": None, "phone": None, "items": [], "total_price": 0}

    if not USER_DETAILS[chat_id].get("name"):
        USER_DETAILS[chat_id]["name"] = text
        save_data()  # Save after storing name
        await update.message.reply_text("📞 Now, please provide your **Phone Number**.")
        return

    if not USER_DETAILS[chat_id].get("phone"):
        USER_DETAILS[chat_id]["phone"] = text
        save_data()  # Save after storing phone number

        # Order Summary
        name = USER_DETAILS[chat_id]["name"]
        phone = USER_DETAILS[chat_id]["phone"]
        total_price = USER_DETAILS[chat_id]["total_price"]
        cart_items = USER_DETAILS[chat_id]["items"]
        cart_summary = "\n".join([f"✅ {item}" for item in cart_items])

        await update.message.reply_text(
            f"✅ **Order Confirmation**\n"
            f"👤 Name: {name}\n"
            f"📞 Phone: {phone}\n"
            f"🛒 Items:\n{cart_summary}\n"
            f"💰 Total: **Birr {total_price}**\n"
            f"🚚 Your order is on the way! Thank you for ordering with Abi Cafe. 🍔"
        )


# Admin Portal Command
async def admin_portal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied. This command is for admins only.")
        return

    await update.message.reply_text(
        "🛠️ **Admin Portal**\n"
        "/view_orders - View all current orders\n"
        "/clear_orders - Clear all orders\n"
        "/announce <message> - Send an announcement to all users"
    )

# View Orders Command
async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied. This command is for admins only.")
        return

    if not USER_DETAILS:
        await update.message.reply_text("📭 No active orders at the moment.")
        return

    order_summary = "**📋 All Current Orders:**\n\n"
    for user_id, details in USER_DETAILS.items():
        if details.get("items"):
            name = details.get("name", "Unknown")
            phone = details.get("phone", "Unknown")
            total_price = details.get("total_price", 0)
            cart_summary = "\n".join([f"✅ {item}" for item in details["items"]])

            order_summary += (
                f"👤 *Name:* {name}\n"
                f"📞 *Phone:* {phone}\n"
                f"🛒 *Items:* \n{cart_summary}\n"
                f"💰 *Total:* Birr {total_price}\n"
                "-----------------------------\n"
            )

    await update.message.reply_text(order_summary, parse_mode='Markdown')


# Clear Orders Command
async def clear_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied. This command is for admins only.")
        return

    USER_ORDERS.clear()
    USER_DETAILS.clear()
    await update.message.reply_text("✅ All orders have been cleared successfully.")

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat_id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied. This command is for admins only.")
        return

    if not context.args:
        await update.message.reply_text("❗ Usage: `/announce <your message>`")
        return

    announcement = "📢 **Announcement:** " + " ".join(context.args)

    # Send the announcement to all known users
    successful_deliveries = 0
    failed_deliveries = 0

    for user_id in USER_LIST:
        try:
            await context.bot.send_message(chat_id=user_id, text=announcement, parse_mode='Markdown')
            successful_deliveries += 1
        except Exception as e:
            print(f"❗ Failed to send message to {user_id}: {e}")
            failed_deliveries += 1

    # Notify the admin about the broadcast status
    await update.message.reply_text(
        f"✅ Announcement sent successfully to {successful_deliveries} user(s).\n"
        f"❌ Failed to deliver to {failed_deliveries} user(s)."
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cart", view_cart))
    app.add_handler(CommandHandler("checkout", checkout))  # Ensure this line matches the indentation
    app.add_handler(CommandHandler("admin", admin_portal))
    app.add_handler(CommandHandler("view_orders", view_orders))
    app.add_handler(CommandHandler("clear_orders", clear_orders))
    app.add_handler(CommandHandler("announce", announce))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_details))
    app.add_handler(CallbackQueryHandler(menu_navigation))

    print("Bot is running...")

    app.run_polling()
