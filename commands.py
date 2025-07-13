import os
import json
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y/%m/%d")
    path = Path("downloads") / today / "metadata.json"

    if not path.exists():
        await update.message.reply_text("No files for today.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    messages = []
    for item in data:
        msg = f"📄 *{item.get('file_name', 'Unknown')}*\n👤 {item.get('user_name', 'Unknown')}\n📁 `{item.get('file_type')}`"
        if item.get('caption'):
            msg += f"\n📝 {item['caption']}"
        messages.append(msg)

    for i in range(0, len(messages), 10):
        await update.message.reply_text(
            "\n\n".join(messages[i:i+10]),
            parse_mode=ParseMode.MARKDOWN
        )


async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use like: /send filename.jpg")
        return

    filename = " ".join(context.args)
    found = None

    for root, _, files in os.walk("downloads"):
        if filename in files:
            found = os.path.join(root, filename)
            break

    if not found:
        await update.message.reply_text("File not found.")
        return

    with open(found, "rb") as f:
        await update.message.reply_document(f, filename=filename)
