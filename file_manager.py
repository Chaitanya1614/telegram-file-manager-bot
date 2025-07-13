import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def save_file(context, file_data, file_type, file_extension, chat_id, message_id, base_dir):
    today = datetime.now().strftime("%Y/%m/%d")
    folder = os.path.join(base_dir, today, file_type)
    os.makedirs(folder, exist_ok=True)

    filename = f"{chat_id}_{message_id}.{file_extension}"
    path = os.path.join(folder, filename)

    try:
        telegram_file = await context.bot.get_file(file_data.file_id)
        await telegram_file.download_to_drive(custom_path=path)
        logger.info(f"Saved file to {path}")
        return path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None


def save_metadata(metadata, base_dir):
    today = datetime.now().strftime("%Y/%m/%d")
    meta_dir = os.path.join(base_dir, today)
    os.makedirs(meta_dir, exist_ok=True)
    meta_path = os.path.join(meta_dir, "metadata.json")

    all_data = []
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        except json.JSONDecodeError:
            logger.warning("Corrupt metadata file, starting fresh.")

    all_data.append(metadata)
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
