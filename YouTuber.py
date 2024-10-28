from flask import Flask, request, jsonify, render_template
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

TOKEN = '8023012612:AAEdZ-lDCA7-FZML48LO6e4jqhLGbXPX0Mk'
flask_app = Flask(__name__, template_folder='/storage/emulated/0/YouTuber/templates')

# Обработчик команды /start для Telegram-бота
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Отправьте мне ссылку на YouTube видео!')

# Обработчик для скачивания видео через Telegram
async def download(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    ydl_opts = {'format': 'best', 'outtmpl': '%(title)s.%(ext)s'}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await update.message.reply_text(f'Видео скачано: {file_path}')
    except Exception as e:
        await update.message.reply_text(f'Ошибка: {str(e)}')

# Регистрируем обработчики
bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/download', methods=['POST'])
def download_from_web():
    data = request.json
    url = data.get('url')
    ydl_opts = {'format': 'best', 'outtmpl': '%(title)s.%(ext)s'}

    try:
        if not url:
            return jsonify({'message': 'URL не указан.'}), 400

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        return jsonify({'message': f'Видео скачано: {file_path}'})
    except Exception as e:
        return jsonify({'message': f'Ошибка: {str(e)}'}), 500

async def run_bot():
    await bot_app.initialize()
    await bot_app.start_polling()

if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)

    # Запуск бота и Flask-приложения
    new_loop.create_task(run_bot())
    flask_app.run(port=5000, debug=True)

