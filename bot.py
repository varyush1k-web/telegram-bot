import telebot
from telebot import types

TOKEN = "8384688345:AAFGh1SVjZZi2qab7mdm6FgblA2Dq6kcu2Y"
ADMIN_ID = 1682893410
CHANNEL_USERNAME = "@posingxd"
PRICE_LINK = "https://t.me/posingxd/7"

bot = telebot.TeleBot(TOKEN)

user_states = {}
orders = {}
messages_waiting = {}

# ---------------- ПРОВЕРКА ПОДПИСКИ ----------------
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

# ---------------- ГЛАВНОЕ МЕНЮ КЛИЕНТА ----------------
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❣️ Заказать позинг")
    markup.add("✉️ Связаться")
    markup.add("💰 Прайс")
    if chat_id == ADMIN_ID:
        markup.add("👩‍💻 В админ панель")
    bot.send_message(chat_id, "Главное меню", reply_markup=markup)

# ---------------- АДМИН МЕНЮ ----------------
def admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤲 Заказы")
    markup.add("✉️ Сообщения")
    markup.add("👤 В меню клиента")
    bot.send_message(chat_id, "Админ панель", reply_markup=markup)

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == ADMIN_ID:
        admin_menu(message.chat.id)
    else:
        main_menu(message.chat.id)

# ---------------- ПЕРЕКЛЮЧЕНИЕ МЕНЮ ----------------
@bot.message_handler(func=lambda m: m.text == "👤 В меню клиента")
def go_client_menu(message):
    main_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "👩‍💻 В админ панель")
def go_admin_menu(message):
    if message.chat.id == ADMIN_ID:
        admin_menu(message.chat.id)

# ---------------- ПРАЙС ----------------
@bot.message_handler(func=lambda m: m.text == "💰 Прайс")
def price(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Открыть прайс 💋", url=PRICE_LINK))
    bot.send_message(message.chat.id, "Нажмите кнопку ниже:", reply_markup=markup)

# ---------------- СВЯЗАТЬСЯ С АДМИНОМ ----------------
@bot.message_handler(func=lambda m: m.text == "✉️ Связаться")
def contact_admin(message):
    bot.send_message(message.chat.id, "Напишите сообщение для админа:")
    user_states[message.chat.id] = "contact_admin"

# ---------------- ОБРАБОТКА СООБЩЕНИЯ К АДМИНУ ----------------
@bot.message_handler(func=lambda m: m.chat.id in user_states)
def handle_message_states(message):
    state = user_states[message.chat.id]

    # ---------------- АНКЕТА ----------------
    if state == "nickname":
        orders[message.chat.id]["nickname"] = message.text
        user_states[message.chat.id] = "deadline"
        bot.send_message(message.chat.id, "2️⃣ Сроки? (срочно / до даты)")
        return

    if state == "deadline":
        orders[message.chat.id]["deadline"] = message.text
        user_states[message.chat.id] = "payment"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("гривны", "робуксы", "еще не знаю")
        bot.send_message(message.chat.id, "3️⃣ Способ оплаты?", reply_markup=markup)
        return

    if state == "payment":
        orders[message.chat.id]["payment"] = message.text
        user_states[message.chat.id] = "wishes"
        bot.send_message(message.chat.id, "4️⃣ Пожелания? (лицо, корблокс, аксессуары, освещение и т.д.)")
        return

    if state == "wishes":
        orders[message.chat.id]["wishes"] = message.text
        user_states[message.chat.id] = "photo1"
        bot.send_message(message.chat.id, "5️⃣ Пришлите фото-пример")
        return

    if state == "contact_admin":
        # Отправляем админу
        bot.send_message(ADMIN_ID, f"📩 Сообщение от {message.chat.id}:\n{message.text}")
        bot.send_message(message.chat.id, "Сообщение отправлено! 💌")
        user_states.pop(message.chat.id)
        return

# ---------------- ЗАКАЗ ----------------
@bot.message_handler(func=lambda m: m.text == "❣️ Заказать позинг")
def make_order(message):
    if not check_subscription(message.chat.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Проверить снова", callback_data="check_sub"))
        bot.send_message(
            message.chat.id,
            "Для оформления заказа подпишитесь на канал @posingxd 💋",
            reply_markup=markup
        )
        return
    user_states[message.chat.id] = "nickname"
    orders[message.chat.id] = {}
    bot.send_message(message.chat.id, "1️⃣ Ваш ник в Roblox?")

# ---------------- ПРОВЕРКА ПОДПИСКИ ----------------
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if check_subscription(call.message.chat.id):
        user_states[call.message.chat.id] = "nickname"
        orders[call.message.chat.id] = {}
        bot.send_message(call.message.chat.id, "Подписка подтверждена!\n\n1️⃣ Ваш ник в Roblox?")
    else:
        bot.answer_callback_query(call.id, "Вы не подписаны 🙁")

# ---------------- ФОТО ----------------
@bot.message_handler(content_types=['photo', 'text'])
def handle_photos(message):
    if message.chat.id not in user_states:
        return
    state = user_states[message.chat.id]

    # Проверяем 5-й и 6-й шаг анкеты
    if state == "photo1":
        if message.content_type != 'photo':
            bot.send_message(message.chat.id, "❗ Отправьте пожалуйста фото")
            return
        orders[message.chat.id]["photo1"] = message.photo[-1].file_id
        user_states[message.chat.id] = "photo2"
        bot.send_message(message.chat.id, "6️⃣ Пришлите фото вашего скина")
        return

    if state == "photo2":
        if message.content_type != 'photo':
            bot.send_message(message.chat.id, "❗ Отправьте пожалуйста фото")
            return
        orders[message.chat.id]["photo2"] = message.photo[-1].file_id
        user_states.pop(message.chat.id)
        bot.send_message(message.chat.id, "Спасибо за заказ! Я скоро свяжусь с вами 💋")
        send_order_to_admin(message.chat.id)

# ---------------- ОТПРАВКА АДМИНУ ----------------
def send_order_to_admin(user_id):
    data = orders[user_id]
    text = f"""📌 Новый заказ

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

# ---------------- ОБРАБОТКА КНОПОК АДМИНА ----------------
@bot.callback_query_handler(func=lambda call: True)
def admin_buttons(call):
    data = call.data
    if data.startswith("reply_"):
        user_id = int(data.split("_")[1])
        bot.send_message(ADMIN_ID, f"Напишите сообщение пользователю {user_id}:")
        user_states[ADMIN_ID] = f"reply_{user_id}"
    elif data.startswith("chat_"):
        user_id = int(data.split("_")[1])
        bot.send_message(ADMIN_ID, f"Открыт чат с пользователем {user_id}")
    elif data.startswith("done_"):
        user_id = int(data.split("_")[1])
        orders.pop(user_id, None)
        bot.edit_message_reply_markup(ADMIN_ID, call.message.message_id, reply_markup=None)
        bot.send_message(ADMIN_ID, f"Заказ {user_id} помечен как готовый ✅")

# ---------------- БЕСКОНЕЧНЫЙ ПУЛЛИНГ ----------------
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout = 60)
    except Exception as e:
        print(f"Ошибка: {e}")
