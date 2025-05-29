import telebot
from telebot import types
import random
import logging
from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

# ыыыыыыыыыы База данных ыыыыыыыы
user_data = {}

class Order:
    def __init__(self):
        self.marketplace = None
        self.warehouse = None
        self.date = None
        self.address = None
        self.distance = None
        self.boxes = None
        self.sender = None
        self.phone = None

    def is_complete(self):
        return all([self.marketplace, self.warehouse, self.date,
                   self.address, self.distance, self.boxes,
                   self.sender, self.phone])

# /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        welcome_text = (
            "🚛 Добро пожаловать в бот для грузоперевозок!\n"
            "Выберите действие:"
        )
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_new = types.KeyboardButton('📝 Новая заявка')
        btn_help = types.KeyboardButton('🆘 Помощь')
        btn_calc = types.KeyboardButton('💰 Расчет стоимости')
        markup.add(btn_new, btn_help, btn_calc)
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
        logger.info(f"User {message.chat.id} started the bot")
    except Exception as e:
        logger.error(f"Error in start: {e}")

# команды обработчики
@bot.message_handler(func=lambda m: m.text in ['📝 Новая заявка', '/new'])
def handle_new_order(message):
    try:
        info_text = (
            "Для создания заявки потребуется указать следующие данные:\n"
            "- Маркетплейс\n"
            "- Склад разгрузки\n"
            "- Необходимая дата разгрузки\n"
            "- Адрес забора поставки\n"
            "- Расстояние от МКАД\n"
            "- Количество коробов\n"
            "- ИП отправителя\n"
            "- Контактный номер телефона отправителя\n\n"
            "Нажмите '🚚 Начать оформление' чтобы продолжить"
        )
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🚚 Начать оформление"))
        
        bot.send_message(
            message.chat.id,
            info_text,
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error in new order: {e}")

@bot.message_handler(func=lambda m: m.text in ['🆘 Помощь', '/help'])
def handle_help(message):
    try:
        help_text = (
            "📞 Контакты поддержки:\n"
            "Если у вас возникли проблемы с ботом или у вас есть вопросы, пожалуйста, свяжитесь с менеджером по номеру: +7 900 123-45-67"

        )
        bot.send_message(message.chat.id, help_text)
    except Exception as e:
        logger.error(f"Error in help: {e}")

@bot.message_handler(func=lambda m: m.text in ['💰 Расчет стоимости', '/calc'])
def handle_calc(message):
    try:
        msg = bot.send_message(
            message.chat.id, 
            "📦 Введите количество коробок:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(msg, process_box_quantity)
    except Exception as e:
        logger.error(f"Error in calc: {e}")

# расчет стоимости
def process_box_quantity(message):
    try:
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "❌ Пожалуйста, введите число!")
            return handle_calc(message)
            
        boxes = int(message.text)
        user_data[message.chat.id] = {'boxes': boxes}
        msg = bot.send_message(
            message.chat.id, 
            "📏 Введите размер одной коробки в формате ДxШxВ (например, 30-20-15 см):"
        )
        bot.register_next_step_handler(msg, process_box_size)
    except Exception as e:
        logger.error(f"Error in box quantity: {e}")

def process_box_size(message):
    try:
        parts = message.text.lower().split('-')
        if len(parts) != 3:
            raise ValueError
            
        length, width, height = map(int, parts)
        volume = length * width * height
        cost = volume * 100  # по сотке за кубометр
        
        response = (
            f"📊 Расчет стоимости:\n"
            f"📦 Размер коробки: {length}x{width}x{height} см\n"
            f"🧮 Объем: {volume} см³\n"
            f"💵 Предварительная стоимость: {cost} руб."
        )
        
        bot.send_message(message.chat.id, response)
        handle_start(message)  # меню
    except:
        bot.send_message(
            message.chat.id, 
            "❌ Неправильный формат! Введите размер как ДxШxВ (например, 30x20x15)"
        )
        handle_calc(message)

# процесс оформления заявы
@bot.message_handler(func=lambda m: m.text == "🚚 Начать оформление")
def start_order_creation(message):
    try:
        user_data[message.chat.id] = Order()
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_ozon = types.KeyboardButton('Ozon')
        btn_wb = types.KeyboardButton('Wildberries')
        markup.add(btn_ozon, btn_wb)
        
        bot.send_message(
            message.chat.id,
            "🛒 Выберите маркетплейс:",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error starting order: {e}")

@bot.message_handler(func=lambda m: m.text in ['Ozon', 'Wildberries'])
def process_marketplace(message):
    try:
        user_data[message.chat.id].marketplace = message.text
        msg = bot.send_message(
            message.chat.id, 
            "🏭 Введите склад разгрузки (например, Склад №1):",
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(msg, process_warehouse)
    except Exception as e:
        logger.error(f"Error processing marketplace: {e}")

def process_warehouse(message):
    try:
        user_data[message.chat.id].warehouse = message.text
        msg = bot.send_message(message.chat.id, "📅 Введите дату разгрузки (в формате ГГГГ-ММ-ДД):")
        bot.register_next_step_handler(msg, process_date)
    except Exception as e:
        logger.error(f"Error processing warehouse: {e}")

def process_date(message):
    try:
        user_data[message.chat.id].date = message.text
        msg = bot.send_message(message.chat.id, "🏠 Введите адрес забора доставки (например, ул. Ленина, д. 1):")
        bot.register_next_step_handler(msg, process_address)
    except Exception as e:
        logger.error(f"Error processing date: {e}")

def process_address(message):
    try:
        user_data[message.chat.id].address = message.text
        msg = bot.send_message(message.chat.id, "📍 Введите расстояние от МКАД (в км):")
        bot.register_next_step_handler(msg, process_distance)
    except Exception as e:
        logger.error(f"Error processing address: {e}")

def process_distance(message):
    try:
        user_data[message.chat.id].distance = message.text
        msg = bot.send_message(message.chat.id, "📦 Введите количество коробов:")
        bot.register_next_step_handler(msg, process_boxes)
    except Exception as e:
        logger.error(f"Error processing distance: {e}")

def process_boxes(message):
    try:
        user_data[message.chat.id].boxes = message.text
        msg = bot.send_message(message.chat.id, "👤 Введите ИП отправителя:")
        bot.register_next_step_handler(msg, process_sender)
    except Exception as e:
        logger.error(f"Error processing boxes: {e}")

def process_sender(message):
    try:
        user_data[message.chat.id].sender = message.text
        msg = bot.send_message(message.chat.id, "📱 Введите контактный телефон отправителя:")
        bot.register_next_step_handler(msg, process_phone)
    except Exception as e:
        logger.error(f"Error processing sender: {e}")

def process_phone(message):
    try:
        user_data[message.chat.id].phone = message.text
        confirm_order(message)
    except Exception as e:
        logger.error(f"Error processing phone: {e}")

def confirm_order(message):
    try:
        order = user_data[message.chat.id]
        
        confirm_text = (
            "✅ Проверьте данные заявки:\n\n"
            f"🛒 Маркетплейс: {order.marketplace}\n"
            f"🏭 Склад: {order.warehouse}\n"
            f"📅 Дата: {order.date}\n"
            f"🏠 Адрес: {order.address}\n"
            f"📍 Расстояние: {order.distance} км\n"
            f"📦 Коробки: {order.boxes}\n"
            f"👤 ИП: {order.sender}\n"
            f"📱 Телефон: {order.phone}\n\n"
            "Всё верно?"
        )
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_confirm = types.KeyboardButton('✅ Подтвердить')
        btn_cancel = types.KeyboardButton('❌ Отменить')
        markup.add(btn_confirm, btn_cancel)
        
        bot.send_message(
            message.chat.id,
            confirm_text,
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error confirming order: {e}")

@bot.message_handler(func=lambda m: m.text == '✅ Подтвердить')
def finish_order(message):
    try:
        order = user_data[message.chat.id]
        order_number = random.randint(1000, 9999)
        
        # Отправка подтверждения пользователю
        bot.send_message(
            message.chat.id,
            f"🎉 Заявка #{order_number} успешно оформлена!\n"
            "📞 С вами свяжется менеджер в ближайшее время.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        # Отправка ADMINY
        admin_chat_id = "1493522735"
        bot.send_message(
            admin_chat_id,
            f"📌 Новая заявка #{order_number}:\n"
            f"👤 Клиент: @{message.from_user.username or 'N/A'}\n"
            f"📱 Телефон: {order.phone}\n"
            f"🛒 Маркетплейс: {order.marketplace}\n"
            f"🏭 Склад: {order.warehouse}\n"
            f"📅 Дата: {order.date}\n"
            f"🏠 Адрес: {order.address}\n"
            f"📦 Коробки: {order.boxes}\n"
            f"👔 ИП: {order.sender}"
        )
        
        del user_data[message.chat.id]
        logger.info(f"Order #{order_number} created by {message.chat.id}")
        handle_start(message)  
    except Exception as e:
        logger.error(f"Error finishing order: {e}")

@bot.message_handler(func=lambda m: m.text == '❌ Отменить')
def cancel_order(message):
    try:
        if message.chat.id in user_data:
            del user_data[message.chat.id]
        bot.send_message(
            message.chat.id,
            "❌ Заявка отменена",
            reply_markup=types.ReplyKeyboardRemove()
        )
        handle_start(message)  
    except Exception as e:
        logger.error(f"Error canceling order: {e}")

if __name__ == '__main__':
    logger.info("Starting bot...")
    try:
        logger.info(f"Using token: {bot.token}")  # Боже это только соло нейросеть, я затупил на логирование
        bot.infinity_polling(logger_level=logging.DEBUG)  
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)  

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    logger.info(f"Received message: {message.text}")
    bot.reply_to(message, f"Echo: {message.text}")


