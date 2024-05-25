import datetime
import config
import rcon
import sqlite3
import telebot
from telebot import types
from telebot.types import LabeledPrice, ShippingOption
import time
import excel

bot = telebot.TeleBot(config.BOT_TOKEN)
prices = [LabeledPrice(label='Проходка на сервер', amount=config.prohodkaprice)]
shipping_options = [
    ShippingOption(id='instant', title='Проходка на сервер').add_price(LabeledPrice(f'Проходка на Minecraft сервер "{config.SERVER_NAME}"', config.prohodkaprice))]
conn = sqlite3.connect('admins.db', check_same_thread=False)
cursor = conn.cursor()

#@bot.message_handler(commands=['updatedatabase'])
#def create(message):
#    cursor.execute('''CREATE TABLE admins (id INTEGER)''')
#    conn.commit()
#    bot.send_message(message.chat.id, 'База данных обновлена!')

@bot.message_handler(commands=['start'])
def start(message):
    kbstart = types.InlineKeyboardMarkup(row_width=1)
    buyprohodkabtn = types.InlineKeyboardButton(text='Купить проходку', callback_data='buyprohodka')
    texsupportbtn = types.InlineKeyboardButton(text='Тех.поддержка', callback_data='texsupport')
    subscribenewsbtn = types.InlineKeyboardButton(text='Подписаться на рассылку', callback_data='subscribenews')
    kbstart.add(buyprohodkabtn, texsupportbtn, subscribenewsbtn)
    bot.send_message(message.chat.id, f'Привет! Это бот {config.SERVER_NAME}, здесь мы можешь купить проходку на сервер', reply_markup=kbstart)

@bot.callback_query_handler(func=lambda callback: callback.data)
def callbackcheck(callback):
    if callback.data == 'buyprohodka':
        bot.send_invoice(
            callback.message.chat.id,  # chat_id
            'Проходка на сервер',  # title
            f'Проходка на Minecraft сервер "{config.SERVER_NAME}"',
            # description
            'MINECRAFT SERVER',  # invoice_payload
            config.PAYMENTS_TOKEN,  # provider_token
            'rub',  # currency
            prices,  # prices
            photo_url=config.invoice_photo_url,
            photo_height=512,  # !=0/None or picture won't be shown
            photo_width=512,
            photo_size=512,
            is_flexible=False,  # True If you need to set up Shipping Fee
            start_parameter='time-machine-example')

    elif callback.data == 'subscribenews':
        with open('chatids.txt', 'a+') as chatids:
            print(callback.message.chat.id, file=chatids)
        bot.send_message(callback.message.chat.id, 'Ты подписался на рассылку!')

    elif callback.data == 'sendmailing':
        cursor.execute(f'SELECT * FROM admins')
        rows = cursor.fetchall()
        admins = str(rows)
        chatidmes = callback.message.chat.id
        chatidmes = str(chatidmes)
        if chatidmes in admins:
            sendmailingmessage = bot.send_message(callback.message.chat.id, 'Введи текст рассылки')
            bot.register_next_step_handler(sendmailingmessage, sendmailing)
        else:
            bot.send_message(callback.message.chat.id, 'У тебя нету доступа к этой функции!')

    elif callback.data == 'sendmessage':
        cursor.execute(f'SELECT * FROM admins')
        rows = cursor.fetchall()
        admins = str(rows)
        chatidmes = callback.message.chat.id
        chatidmes = str(chatidmes)
        if chatidmes in admins:
            sendmessagemessage = bot.send_message(callback.message.chat.id, 'Введи ID для сообщения')
            bot.register_next_step_handler(sendmessagemessage, getmessage)
        else:
            bot.send_message(callback.message.chat.id, 'У тебя нету доступа к этой функции!')

    elif callback.data == 'texsupport':
        texsupportmessage = bot.send_message(callback.message.chat.id, 'Отправь свой вопрос')
        bot.register_next_step_handler(texsupportmessage, texsupportvopros)

    elif callback.data == 'sendmessagetoadmin':
        sendmessagetoadminmessage = bot.send_message(callback.message.chat.id, 'Отправь ответ на сообщение')
        bot.register_next_step_handler(sendmessagetoadminmessage, otvetmessageadmin)

def sendmailing(message):
    global sendmailingmessage
    sendmailingmessage = message
    bot.send_message(message.chat.id, '✅Рассылка начата!✅')
    for i in open('chatids.txt', 'r').readlines():
        time.sleep(0.5)
        try:
            bot.copy_message(i, sendmailingmessage.chat.id, sendmailingmessage.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass

    bot.send_message(message.chat.id, '✅Рассылка завершена!✅')

def getmessage(message):
    global messageuserid
    messageuserid = message
    getmessagemessage = bot.send_message(message.chat.id, 'Введи сообщение')
    bot.register_next_step_handler(getmessagemessage, sendmessage)

def sendmessage(message):
    global messagetouser
    messagetouser = message
    kbotver = types.InlineKeyboardMarkup(row_width=1)
    otvetbutton = types.InlineKeyboardButton(text='Ответить', callback_data='sendmessagetoadmin')
    kbotver.add(otvetbutton)
    bot.send_message(messageuserid.chat.id, 'Новое сообщение!\nДля ответа используй кнопку ниже', reply_markup=kbotver)
    bot.copy_message(messageuserid.chat.id, message.chat.id, messagetouser.message_id)
    bot.send_message(message.chat.id, 'Сообщение отправлено!')

def texsupportvopros(message):
    global texsupportvoprosmsg
    texsupportvoprosmsg = message
    bot.send_message(config.GROUP_CHAT_ID, f'Человек обратился в тех.поддержку\nChatID: {message.chat.id}\nUserName: @{message.from_user.username}\nСообщение ниже')
    bot.copy_message(config.GROUP_CHAT_ID, message.chat.id, texsupportvoprosmsg.message_id)
    bot.send_message(message.chat.id, 'Твоё обращение отправлено!')

def otvetmessageadmin(message):
    global otvetmessageadmimessage
    otvetmessageadmimessage = message
    bot.send_message(config.GROUP_CHAT_ID, f'Ответил человек с ID: {message.chat.id}')
    bot.copy_message(config.GROUP_CHAT_ID, message.chat.id, otvetmessageadmimessage.message_id)
    bot.send_message(message.chat.id, 'Твой ответ отправлен!')

@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options, error_message='Чето не так, попробуй потом')

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message='Чето не так, попробуй потом')

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    getnicknamemessage = bot.send_message(message.chat.id, 'Отправь мне свой ник в Minecraft')
    bot.register_next_step_handler(getnicknamemessage, addwlistplayer)

def addwlistplayer(message):
    nicknameplayer = message.text
    try:
        rcon.addplayertowhitelist(nickname=nicknameplayer)
        bot.send_message(message.chat.id, f'Я добавил тебя в белый список!\nIP сервера: {config.serveripandport}')
        datalistbuys = [f'{nicknameplayer}', 'Проходку', f'{datetime.datetime.now()}', f'{message.chat.id}', f'{message.from_user.username}']
        excel.pastedata(datalistbuys)
    except OSError:
        bot.send_message(message.chat.id, 'Не удалось добавить тебя в белый список!\nНапиши в поддержку!')

@bot.message_handler(commands=['addadmin'])
def getadminchatid(message):
    if message.chat.id == config.OWNER_CHAT_ID:
        getadminchatidmessage = bot.send_message(message.chat.id, 'Введи ID будущего админа')
        bot.register_next_step_handler(getadminchatidmessage, addadmin)
    else:
        bot.send_message(message.chat.id, 'Ты не админ!')

def addadmin(message):
    global adminchatid
    adminchatid = int(message.text)
    user_data = (adminchatid,)
    cursor.execute('''INSERT INTO admins (id) VALUES (?)''', user_data)
    conn.commit()
    bot.send_message(message.chat.id, 'Админ добавлен')

@bot.message_handler(commands=['admin'])
def admin(message):
    cursor.execute(f'SELECT * FROM admins')
    rows = cursor.fetchall()
    admins = str(rows)
    chatidmes = message.chat.id
    chatidmes = str(chatidmes)
    if chatidmes in admins:
        kbadmin = types.InlineKeyboardMarkup(row_width=1)
        sendmailingbutton = types.InlineKeyboardButton(text='Рассылка', callback_data='sendmailing')
        sendmessagebutton = types.InlineKeyboardButton(text='Отправить сообщение', callback_data='sendmessage')
        kbadmin.add(sendmailingbutton, sendmessagebutton)
        bot.send_message(message.chat.id, 'Админ панель', reply_markup=kbadmin)
    else:
        bot.send_message(message.chat.id, 'У тебя нету доступа к этой функции!')

@bot.message_handler(commands=['addplayerinwhitelist'])
def addplayerinwhitelist(message):
    cursor.execute(f'SELECT * FROM admins')
    rows = cursor.fetchall()
    admins = str(rows)
    chatidmes = message.chat.id
    chatidmes = str(chatidmes)
    if chatidmes in admins:
        nickname = message.text
        nickname = nickname.replace('/addplayerinwhitelist ', '')
        addplayer = rcon.addplayertowhitelist(nickname=nickname)
        bot.send_message(message.chat.id, addplayer)
    else:
        bot.send_message(message.chat.id, 'У тебя нету доступа к этой функции!')

@bot.message_handler(commands=['removeplayerfromwhitelist'])
def removeplayerfromwhitelist(message):
    cursor.execute(f'SELECT * FROM admins')
    rows = cursor.fetchall()
    admins = str(rows)
    chatidmes = message.chat.id
    chatidmes = str(chatidmes)
    if chatidmes in admins:
        nickname = message.text
        nickname = nickname.replace('/removeplayerfromwhitelist ', '')
        remplayer = rcon.removeplayerfronwhitelist(nickname=nickname)
        bot.send_message(message.chat.id, remplayer)
    else:
        bot.send_message(message.chat.id, 'У тебя нету доступа к этой функции!')

@bot.message_handler(commands=['getwhitelist'])
def removeplayerfromwhitelist(message):
    cursor.execute(f'SELECT * FROM admins')
    rows = cursor.fetchall()
    admins = str(rows)
    chatidmes = message.chat.id
    chatidmes = str(chatidmes)
    if chatidmes in admins:
        whitelist = rcon.getwhitelistlist()
        bot.send_message(message.chat.id, whitelist)
    else:
        bot.send_message(message.chat.id, 'У тебя нету доступа к этой функции!')

@bot.message_handler(commands=['getexceltable'])
def getexceltable(message):
    cursor.execute(f'SELECT * FROM admins')
    rows = cursor.fetchall()
    admins = str(rows)
    chatidmes = message.chat.id
    chatidmes = str(chatidmes)
    if chatidmes in admins:
        shoptable = open('shop.xlsx', 'rb')
        bot.send_document(message.chat.id, shoptable)
    else:
        bot.send_message(message.chat.id, 'У тебя нету доступа к этой функции!')

bot.polling(non_stop=True)