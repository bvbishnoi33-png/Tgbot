# bot.py
# Telegram bot with daily usage limit + admin unlimited access

import subprocess
import re
import json
import os
from datetime import date
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==============================
# 🔑 BOT CONFIG
# ==============================
BOT_TOKEN = "8216040234:AAFVxhT9sbPEx_xyldANaY6obAdNDm_bxmU"

ADMIN_USERNAME = "@unknownbishnoi07"
ADMIN_TELEGRAM_ID = 5933760251     # <-- PUT YOUR TELEGRAM NUMERIC ID
DAILY_LIMIT = 5                  # change to 10 if you want
USAGE_FILE = "usage.json"

# ==============================
# 🇮🇳 Indian mobile number validation
# ==============================
def is_valid_indian_number(number: str) -> bool:
    return number.isdigit() and len(number) == 10 and number[0] in "6789"

# ==============================
# 🔐 Run encrypted script safely
# ==============================
import subprocess
import tempfile
import re

def run_encrypted_script(number: str):
    try:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            input_file = f.name
            f.write(number + "\n")

        process = subprocess.run(
            ["python3", "secure_lookup.py"],
            stdin=open(input_file),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
            env={
                **os.environ,
                "NO_COLOR": "1",
                "COLORAMA_FORCE_STRIP": "1",
                "TERM": "xterm"
            }
        )

        output = process.stdout or process.stderr
        if not output:
            return None

        if "RESULTS :" in output:
            output = output.split("RESULTS :", 1)[1]

        output = re.sub(r"ENTER.*?(EXIT.*?\))", "", output, flags=re.I | re.S)
        output = re.sub(r"[=\-]{5,}", "", output)
        output = re.sub(r"\n{3,}", "\n\n", output)

        return output.strip()

    except subprocess.TimeoutExpired:
        return "⚠️ Lookup timed out."
# ==============================
# 🧹 Clean output for Telegram
# ==============================
def clean_output(text: str) -> str:
    text = re.sub(r"[=\-]{5,}", "", text)

    text = re.sub(
        r"ENTER.*?(EXIT.*?\))",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# ==============================
# 📊 Usage tracking (daily limit)
# ==============================
def load_usage():
    if not os.path.exists(USAGE_FILE):
        return {"date": str(date.today()), "users": {}}

    with open(USAGE_FILE, "r") as f:
        data = json.load(f)

    if data.get("date") != str(date.today()):
        return {"date": str(date.today()), "users": {}}

    return data


def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)


def can_user_search(user_id: int) -> bool:
    if user_id == ADMIN_TELEGRAM_ID:
        return True

    data = load_usage()
    return data["users"].get(str(user_id), 0) < DAILY_LIMIT


def increment_usage(user_id: int):
    if user_id == ADMIN_TELEGRAM_ID:
        return

    data = load_usage()
    uid = str(user_id)
    data["users"][uid] = data["users"].get(uid, 0) + 1
    save_usage(data)

# ==============================
# ▶️ /start command
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 *Welcome to the NUM LOOKUP BOT*\n"
        f"*By {ADMIN_USERNAME}*\n\n"
        "📱 Send any *Indian mobile number* (without +91)"
        "to get its details.\n\n"
        "⚠️ *Disclaimer:*\n"
        "• For educational purposes only\n"
        "• Information provided here may not be correct\n"
        "• Admin/Owner of this bot is not responsible for any loss",
    
    )

# ==============================
# 📩 Handle user messages
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    number = update.message.text.strip()

    # Daily limit check
    if not can_user_search(user_id):
        await update.message.reply_text(
            f"🚫 *Daily limit reached*\n\n"
            f"You can perform only *{DAILY_LIMIT} searches per day*.\n"
            f"Please try again tomorrow.\n\n"
            f"Contact Admin for Premium Subscription.\n\n"
            f"👮 *ADMIN* : {ADMIN_USERNAME}",
        )
        return

    if not is_valid_indian_number(number):
        await update.message.reply_text(
            "❌ Invalid number.\n"
            "Please send a valid 10-digit Indian mobile number."
        )
        return

    await update.message.reply_text("🔍 Searching private database...")

    result = run_encrypted_script(number)

    if not result:
        await update.message.reply_text(
            "⚠️ No record found in private database."
        )
        return

    increment_usage(user_id)

    cleaned = clean_output(result)

    final_message = (
        "📊 *Lookup Result*\n\n"
        f"{cleaned}\n\n"
        f"👮 *ADMIN* : {ADMIN_USERNAME}\n\n"
        "✅ Shared with prior consent\n"
        "⚠️ Personal & educational use only"
    )

    await update.message.reply_text(final_message)

# ==============================
# 🚀 Main runner
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
