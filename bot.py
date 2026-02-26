import telebot
from telebot import types

TOKEN = "8384688345:AAFGh1SVjZZi2qab7mdm6FgblA2Dq6kcu2Y"
ADMIN_ID = 1682893410
CHANNEL_USERNAME = "@posingxd"

bot = telebot.TeleBot(TOKEN)

user_states = {}
orders = {}
active_chats = {}
messages_waiting = {}

# ---------------- ПРОВЕРКА ПОДПИСКИ ----------------

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

# ---------------- ГЛАВНОЕ МЕНЮ ----------------

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❣️ Заказать позинг")
    markup.add("✉️ Связаться")
    markup.add("💰 Прайс")
    bot.send_message(chat_id, "Главное меню", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == ADMIN_ID:
        admin_menu(message.chat.id)
    else:
        main_menu(message.chat.id)

# ---------------- АДМИН МЕНЮ ----------------

def admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤲 Заказы")
    markup.add("✉️ Сообщения")
    bot.send_message(chat_id, "Админ панель", reply_markup=markup)

# ---------------- ЗАКАЗ ----------------

@bot.message_handler(func=lambda m: m.text == "❣️ Заказать позинг")
def make_order(message):
    if not check_subscription(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Проверить снова", callback_data="check_sub"))
        bot.send_message(message.chat.id,
                         "Для оформления заказа подпишитесь на канал @posingxd 💋",
                         reply_markup=markup)
        return

    user_states[message.chat.id] = "nickname"
    orders[message.chat.id] = {}
    bot.send_message(message.chat.id, "1️⃣ Ваш ник в Roblox?")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if check_subscription(call.message.chat.id):
        user_states[call.message.chat.id] = "nickname"
        orders[call.message.chat.id] = {}
        bot.send_message(call.message.chat.id, "Подписка подтверждена!\n\n1️⃣ Ваш ник в Roblox?")
    else:
        bot.answer_callback_query(call.id, "Вы не подписаны!🙁")

# ---------------- ОБРАБОТКА АНКЕТЫ ----------------

@bot.message_handler(func=lambda m: m.chat.id in user_states)
def handle_form(message):
    state = user_states[message.chat.id]

    if state == "nickname":
        orders[message.chat.id]["nickname"] = message.text
        user_states[message.chat.id] = "deadline"
        bot.send_message(message.chat.id, "2️⃣ Сроки? (срочно / до даты)")

    elif state == "deadline":
        orders[message.chat.id]["deadline"] = message.text
        user_states[message.chat.id] = "payment"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("гривны", "робуксы", "еще не знаю")
        bot.send_message(message.chat.id, "3️⃣ Способ оплаты?", reply_markup=markup)

    elif state == "payment":
        orders[message.chat.id]["payment"] = message.text
        user_states[message.chat.id] = "wishes"
        bot.send_message(message.chat.id, "4️⃣ Пожелания? (лицо, корблокс, аксессуары, освещение и т.д.)")

    elif state == "wishes":
        orders[message.chat.id]["wishes"] = message.text
        user_states[message.chat.id] = "photo1"
        bot.send_message(message.chat.id, "5️⃣ Пришлите фото-пример")

# ---------------- ПРОВЕРКА ФОТО ----------------

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    if message.chat.id not in user_states:
        return

    state = user_states[message.chat.id]

    if state == "photo1":
        orders[message.chat.id]["photo1"] = message.photo[-1].file_id
        user_states[message.chat.id] = "photo2"
        bot.send_message(message.chat.id, "6️⃣ Пришлите фото вашего скина")

    elif state == "photo2":
        orders[message.chat.id]["photo2"] = message.photo[-1].file_id
        user_states.pop(message.chat.id)

        bot.send_message(message.chat.id, "Спасибо за заказ! Я скоро свяжусь с вами💋")
        send_order_to_admin(message.chat.id)

def send_order_to_admin(user_id):
    data = orders[user_id]
    text = f"""📌 Новый заказ!

ID: {user_id}
Ник: {data['nickname']}
Сроки: {data['deadline']}
Оплата: {data['payment']}
Пожелания: {data['wishes']}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✉️ Ответить", callback_data=f"reply_{user_id}"))
    markup.add(types.InlineKeyboardButton("💬 Чат", callback_data=f"chat_{user_id}"))
    markup.add(types.InlineKeyboardButton("✅ Готов", callback_data=f"done_{user_id}"))

    bot.send_message(ADMIN_ID, text, reply_markup=markup)
    bot.send_photo(ADMIN_ID, data["photo1"])
    bot.send_photo(ADMIN_ID, data["photo2"])

# ---------------- ЗАПУСК ----------------

bot.polling(none_stop=True)