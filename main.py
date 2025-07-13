import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from config import TELEGRAM_BOT_TOKEN, DOWNLOAD_BASE_DIR
from file_manager import save_file, save_metadata
from commands import list_files, send_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_file_info(message):
    if message.photo:
        file_data = message.photo[-1]
        return {
            'telegram_object': file_data,
            'file_id': file_data.file_id,
            'type': 'image',
            'extension': 'jpg',
            'name': None,
            'size': file_data.file_size
        }
    elif message.video:
        file_data = message.video
        return {
            'telegram_object': file_data,
            'file_id': file_data.file_id,
            'type': 'video',
            'extension': 'mp4',
            'name': file_data.file_name,
            'size': file_data.file_size
        }
    elif message.document:
        file_data = message.document
        extension = file_data.file_name.split('.')[-1] if file_data.file_name else 'bin'
        return {
            'telegram_object': file_data,
            'file_id': file_data.file_id,
            'type': 'document',
            'extension': extension,
            'name': file_data.file_name,
            'size': file_data.file_size
        }
    elif message.audio:
        file_data = message.audio
        return {
            'telegram_object': file_data,
            'file_id': file_data.file_id,
            'type': 'audio',
            'extension': 'mp3',
            'name': file_data.file_name,
            'size': file_data.file_size
        }
    return None


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    file_info = extract_file_info(message)
    if not file_info:
        return

    saved_path = await save_file(
        context=context,
        file_data=file_info['telegram_object'],
        file_type=file_info['type'],
        file_extension=file_info['extension'],
        chat_id=chat.id,
        message_id=message.message_id,
        base_dir=DOWNLOAD_BASE_DIR
    )

    if saved_path:
        metadata = {
            "file_name": file_info['name'] or os.path.basename(saved_path),
            "saved_path": saved_path,
            "user_name": user.full_name,
            "user_id": user.id,
            "chat_id": chat.id,
            "file_type": file_info['type'],
            "caption": message.caption or "",
        }
        save_metadata(metadata, DOWNLOAD_BASE_DIR)


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("send", send_file))

    media_filter = filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO
    app.add_handler(MessageHandler(media_filter, handle_media))

    app.run_polling()


if __name__ == '__main__':
    main()
