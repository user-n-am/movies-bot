from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import requests
from urllib.parse import quote

# =========================
# YOUR TELEGRAM BOT TOKEN
# =========================
TOKEN = "8850104490:AAF1qiq9DqbyQMjA_-VHNpY8mX_o5NlyMzE"
CHANNEL_USERNAME = "@entertainmentonlyyy"
# =========================
# OMDb API KEY
# =========================
API_KEY = "564727fa"

async def check_join(update, context):

    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        if member.status in ["member", "administrator", "creator"]:
            return True

        return False

    except:
        return False
# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    joined = await check_join(update, context)

    if not joined:

        await update.message.reply_text(
            f"🚫 First join our channel:\n"
            f"{CHANNEL_USERNAME}\n\n"
            f"Then send /start again."
        )

        return

    await update.message.reply_text(
        "✅ You joined successfully!\n\n"
        "🎬 Send movie or series name."
    )


# =========================
# SEARCH MOVIE FUNCTION
# =========================
async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):

    joined = await check_join(update, context)

    if not joined:

        await update.message.reply_text(
            f"🚫 Join channel first:\n{CHANNEL_USERNAME}"
        )

        return

    query = update.message.text.strip()

    # Search movies
    search_url = f"http://www.omdbapi.com/?apikey={API_KEY}&s={quote(query)}"

    search_response = requests.get(search_url)
    search_data = search_response.json()

    # If no movie found
    if search_data.get("Response") != "True":
        await update.message.reply_text(
            "❌ Movie or series not found.\nTry full title."
        )
        return

    # Take first result
    first_result = search_data["Search"][0]

    imdb_id = first_result["imdbID"]

    # Get full details
    detail_url = (
        f"http://www.omdbapi.com/?apikey={API_KEY}"
        f"&i={imdb_id}&plot=full"
    )

    detail_response = requests.get(detail_url)
    data = detail_response.json()

    # Movie details
    title = data.get("Title", "Unknown")
    year = data.get("Year", "Unknown")
    rating = data.get("imdbRating", "N/A")
    genre = data.get("Genre", "N/A")
    plot = data.get("Plot", "N/A")
    poster = data.get("Poster", "")

    # Message format
    message = (
        f"🎬 {title}\n\n"
        f"📅 Year: {year}\n"
        f"⭐ IMDb Rating: {rating}\n"
        f"🎭 Genre: {genre}\n\n"
        f"📝 Plot:\n{plot}"
    )

    # Send poster if available
    if poster != "N/A" and poster != "":
        await update.message.reply_photo(
            photo=poster,
            caption=message
        )
    else:
        await update.message.reply_text(message)


# =========================
# MAIN BOT
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        search_movie
    )
)

print("✅ Bot is running...")

app.run_polling()