import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Устанавливаем токен вашего бота
BOT_TOKEN = '5180483481:AAEK1DOTkHNmu5tnaLRs0k5CNAAYr2yiE7c'

# Настройки для подключения к базе данных
DB_PATH = 'wallets.db'

# Включаем логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Функция для обработки команд /start
def start(update: Update, context):
    update.message.reply_text('Добро пожаловать в бота! Используйте команду /create_wallet для создания нового кошелька.')

# Функция для обработки команды /create_wallet
def create_wallet(update: Update, context):
    # Генерация нового кошелька TON
    wallet_data = generate_ton_wallet()
    if not wallet_data:
        update.message.reply_text("Ошибка при создании кошелька.")
        return
    
    address = wallet_data['address']
    mnemonic = " ".join(wallet_data['mnemonics'])
    
    # Сохраняем данные кошелька в базе данных
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO wallets (user_id, address, mnemonic) VALUES (?, ?, ?)', 
                   (str(update.message.from_user.id), address, mnemonic))
    conn.commit()
    conn.close()

    # Отправляем информацию пользователю
    update.message.reply_text(f"Ваш новый кошелек создан!\nАдрес: {address}\nМнемоническая фраза: {mnemonic}")
    
    # Получаем баланс кошелька
    balance = get_ton_balance(address)
    update.message.reply_text(f"Баланс вашего кошелька: {balance} TON")

# Обработчик webhook для получения обновлений от Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    # Получаем данные от Telegram
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot)
    
    # Запускаем обработку команды
    dispatcher.process_update(update)
    
    return '', 200

# Устанавливаем webhook
def set_webhook():
    url = 'https://<YOUR_VERCEL_URL>/webhook'
    bot.set_webhook(url=url)

# Главная функция
if __name__ == '__main__':
    # Настройка диспетчера
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("create_wallet", create_wallet))

    # Устанавливаем webhook
    set_webhook()
    
    # Запускаем Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
