import os 
import time
import queue
import asyncio
from utils import *
from config import *
from html import escape
from pyrogram import idle
from pyromod import listen
from pyrogram.errors import FloodWait
from pyrogram import Client, filters, enums
from asyncio import get_event_loop
from status import *

DOWNLOAD_PATH = "downloads/"
loop = get_event_loop()

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

user_data = {}
TOKEN_TIMEOUT = 7200

# Create a global task queue
task_queue = queue.Queue()
initial_messages = {}  # Store initial messages for progress updates

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN, 
    workers=1000, 
    parse_mode=enums.ParseMode.HTML
)

async def worker():
    while True:
        message = await loop.run_in_executor(None, task_queue.get)
        if message is None:
            break  # Exit if a sentinel value is received
        
        await forward_message_to_new_channel(app, message)
        task_queue.task_done()

async def main():
    # Start the worker
    loop.create_task(worker())
    
    async with app:
        await idle()

with app:
    bot_username = (app.get_me()).username

@app.on_message(filters.private & (filters.document | filters.video))
async def enqueue_message(client, message):
    # Send an initial message when a new task is added to the queue
    initial_msg = await message.reply_text("📥 Preparing to download your file...")

    # Add the message and the initial message reference to the task queue
    task_queue.put((message, initial_msg))
    initial_messages[message.id] = initial_msg  # Store reference for later updates

async def forward_message_to_new_channel(client, message_tuple):
    try:
        message, initial_msg = message_tuple  # Unpack the tuple
        media = message.document or message.video
        file_id = message.id
        file_size = media.file_size

        if media:
            caption = message.caption if message.caption else None

            if caption:
                new_caption = await remove_unwanted(caption)
                cap_no_ext = await remove_extension(new_caption)

                logger.info(f"Downloading initial part of {file_id}...")

                reset_progress()
                file_path = await app.download_media(message, file_name=f"{new_caption}", 
                                                     progress=progress,
                                                     progress_args=("Download", initial_msg)
                                                     )

                # Generating Thumbnail
                movie_name, release_year = await extract_movie_info(cap_no_ext)
                thumbnail_path = await get_movie_poster(movie_name, release_year)
                duration = await generate_duration(file_path)

                if thumbnail_path:
                    logger.info(f"Thumbnail generated: {thumbnail_path}")
                else:
                    logger.info("Failed to generate thumbnail")

                upld_msg = await initial_msg.edit_text("⏫ Uploading")

                reset_progress()
                send_msg = await app.send_video(
                    DB_CHANNEL_ID,
                    video=file_path,
                    caption=f"<code>{escape(new_caption)}</code>",
                    duration=duration,
                    width=480,
                    height=320,
                    thumb=thumbnail_path,
                    progress=progress,
                    progress_args=("Upload", upld_msg)
                )

                await upld_msg.edit_text("Uploaded ✅")

                file_link  = f"https://thetgflix.sshemw.workers.dev/bot1/{send_msg.id}"
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📥 Get File", url=file_link)]])
                await app.send_photo(CAPTION_CHANNEL_ID, thumbnail_path, caption=file_info, reply_markup=keyboard)

                os.remove(thumbnail_path)
                os.remove(file_path)

                await asyncio.sleep(3)

    except Exception as e:
        logger.error(f'{e}') 
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        if message.id in initial_messages:
            del initial_messages[message.id]  # Clean up the initial message reference

@app.on_message(filters.command("start"))
async def get_command(client, message):
    reply = await message.reply_text(f"<b>💐Welcome this is TG⚡️Flix Bot")
    await auto_delete_message(message, reply)

# Get Log Command
@app.on_message(filters.command("log") & filters.user(OWNER_USERNAME))
async def log_command(client, message):
    user_id = message.from_user.id

    # Send the log file
    try:
        reply = await app.send_document(user_id, document=LOG_FILE_NAME, caption="Bot Log File")
        await auto_delete_message(message, reply)
    except Exception as e:
        await app.send_message(user_id, f"Failed to send log file. Error: {str(e)}")
    
if __name__ == "__main__":
    logger.info("Bot is starting...")
    loop.run_until_complete(main())
    logger.info("Bot has stopped.")
