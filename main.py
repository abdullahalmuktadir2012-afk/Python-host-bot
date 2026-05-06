import os
import subprocess
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Railway ENV variable theke token nibe
TOKEN = os.getenv("BOT_TOKEN")

# ===== MENU =====
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Run Python", callback_data="run")],
        [InlineKeyboardButton("📊 Status", callback_data="status")]
    ])

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Railway Host Bot Ready!", reply_markup=menu())

# ===== BUTTON =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "run":
        await q.edit_message_text("📤 Send your .py file", reply_markup=menu())

    elif q.data == "status":
        await q.edit_message_text("✅ Bot is running on Railway\n⏱ Timeout: 5 sec", reply_markup=menu())

# ===== FILE RUN =====
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not doc.file_name.endswith(".py"):
        await update.message.reply_text("❌ Only .py file allowed")
        return

    file = await doc.get_file()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        await file.download_to_drive(tmp.name)
        path = tmp.name

    try:
        result = subprocess.run(
            ["python", path],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout or result.stderr or "✅ No output"

    except subprocess.TimeoutExpired:
        output = "⏱ Timeout (5 sec)"

    except Exception as e:
        output = f"❌ Error: {e}"

    await update.message.reply_text(f"```\n{output[:4000]}\n```", parse_mode="Markdown")

    os.remove(path)

# ===== MAIN =====
def main():
    if not TOKEN:
        print("❌ BOT_TOKEN not set!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("🚀 Bot running on Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()