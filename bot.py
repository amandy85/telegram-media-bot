import os
import tempfile
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import yt_dlp 
import requests

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get token from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user = update.effective_user
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("Please send a valid URL")
        return

    try:
        await update.message.reply_text("⏳ Processing your request...")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            ydl_opts = {
                'outtmpl': os.path.join(tmp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                ydl.process_info(info)

                # Determine media type
                if info['ext'] in ['mp4', 'mkv', 'webm']:
                    await update.message.reply_video(video=open(filename, 'rb'))
                elif info['ext'] in ['jpg', 'jpeg', 'png', 'webp']:
                    await update.message.reply_photo(photo=open(filename, 'rb'))
                else:
                    await update.message.reply_document(document=open(filename, 'rb'))

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    if not TOKEN:
        logging.error("❌ Telegram token not found in environment variables!")
        return
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()