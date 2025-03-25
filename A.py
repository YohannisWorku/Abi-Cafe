from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import random

# Replace with your NEW secure bot token
BOT_TOKEN = "Your token"

# Sample image source (e.g., Unsplash API or similar free image sources)
IMAGE_API_URL = "https://picsum.photos/600/400"
CHOICE_KEYBOARD = ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True)

# Inline keyboard with a 'Like' button
def like_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("👍 Like", callback_data="like")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Picture Bot! 📷\n"
        "Send /random to get a random picture or type a keyword for themed images."
    )

async def fetch_image_url(image_url):
    """Fetch image URL and ensure it's valid."""
    try:
        response = requests.get(image_url)
        if response.headers.get('content-type') in ['image/jpeg', 'image/png']:
            return response.url
        else:
            return None
    except Exception:
        return None

async def random_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_url = await fetch_image_url(IMAGE_API_URL)
    if image_url:
        await update.message.reply_photo(photo=image_url, reply_markup=like_button())
    else:
        await update.message.reply_text("❌ Sorry, couldn't fetch a valid image right now. Please try again later.")

async def image_by_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword = " ".join(context.args)
    if not keyword:
        await update.message.reply_text("Please provide a keyword after the command. Example: /keyword sunset")
        return

    search_url = f"https://source.unsplash.com/600x400/?{keyword}"
    image_url = await fetch_image_url(search_url)

    if image_url:
        await update.message.reply_photo(photo=image_url, reply_markup=like_button())
    else:
        await update.message.reply_text(f"❌ No valid image found for '{keyword}'. Please try another keyword.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword = update.message.text.strip()
    search_url = f"https://source.unsplash.com/600x400/?{keyword}"
    image_url = await fetch_image_url(search_url)

    if image_url:
        await update.message.reply_photo(photo=image_url, reply_markup=like_button())
    else:
        await update.message.reply_text(f"❌ No valid image found for '{keyword}'. Please try another keyword.")

# Handle the 'Like' button click
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    if query.data == "like":
        await query.edit_message_reply_markup(reply_markup=None)  # Remove the 'Like' button
        await query.message.reply_text("❤️ Thanks for your feedback!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_image))
    app.add_handler(CommandHandler("keyword", image_by_keyword))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Handle callback queries (for button clicks)
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")

    # Prevent multiple instances
    try:
        app.run_polling()
    except telegram.error.Conflict:
        print("Another instance is already running. Terminating this one.")
