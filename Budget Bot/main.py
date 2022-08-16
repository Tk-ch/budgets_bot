import telebot, pickle, atexit
from user import User, users
from conf import API_KEY

bot = telebot.TeleBot(API_KEY)

with open('data.p', 'rb') as fp:
    users = pickle.load(fp)

def save_users():
    for user in users:
        users[user].cmd = {}
        users[user].questions = []
    with open('data.p', 'wb') as fp:
        pickle.dump(users, fp, protocol=pickle.HIGHEST_PROTOCOL)

def makeUser(chat):
    if chat in users:
        return users[chat]
    user = User()
    user.chat = chat
    users[chat] = user
    return user

def setup(message):
    text = message.text
    user = makeUser(message.chat.id)
    return (text, user)

@bot.message_handler()
def handle(message):
    text, user = setup(message)
    text = text.lstrip('/')
    msg, markup = user.parse(text)
    bot.send_message(user.chat, msg, reply_markup=markup)
    
atexit.register(save_users)
bot.infinity_polling(skip_pending = True)