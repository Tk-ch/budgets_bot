import telebot, pickle, atexit
from user import User, users
from conf import API_KEY, DATA

bot = telebot.TeleBot(API_KEY)

with open(DATA, 'rb') as fp:
    users = pickle.load(fp)

def save_users():
    for user in users:
        users[user].commandData = {}
        users[user].command = None
    with open(DATA, 'wb') as fp:
        pickle.dump(users, fp, protocol=pickle.HIGHEST_PROTOCOL)

def make_user(chat):
    if chat in users:
        return users[chat]
    user = User()
    user.chat = chat
    users[chat] = user
    return user

def setup(message):
    text = message.text
    user = make_user(message.chat.id)
    return (text, user)

messages_to_delete = []

@bot.message_handler(content_types=['text'])
def handle(message):
    global messages_to_delete
    text, user = setup(message)
    text = text.lstrip('/')
    msg_info = user.parse(text)
    send_message(user, msg_info)
    if (msg_info.delete_users_message): 
        bot.delete_message(message.chat.id, message.message_id)
    if len(messages_to_delete) > 0:
        for message in messages_to_delete:
            bot.delete_message(message.chat.id, message.message_id)
        messages_to_delete = []

def send_message(user, message_info): 
    global messages_to_delete
    msg = bot.send_message(user.chat, message_info.text, reply_markup=message_info.markup)
    if message_info.delete:
        messages_to_delete.append(msg)

  
atexit.register(save_users)
bot.infinity_polling(skip_pending = True)