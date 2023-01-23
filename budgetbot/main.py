import telebot, pickle, atexit
from user import User, users
from conf import API_KEY, DATA
from cmdFunctions import getMarkup

bot = telebot.TeleBot(API_KEY)

with open(DATA, 'rb') as fp:
    users = pickle.load(fp)

def save_users():
    for user in users:
        users[user].commandData = {}
        users[user].command = None
    with open(DATA, 'wb') as fp:
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

@bot.message_handler(content_types=['text'])
def handle(message):
    text, user = setup(message)
    text = text.lstrip('/')
    msg_info = user.parse(text)
    sendMessage(user, msg_info)
    
    
def sendMessage(user, message_info):
  msg = bot.send_message(user.chat, message_info.text, message_info.markup)
  if message_info.delete:
    bot.register_next_step_handler(msg, deleteMessage)
  if message_info.reset_markup:
    telebot.apihelper.call_later(15, reset_markup, msg, user)

def deleteMessage(msg):
  bot.delete_message(msg.chat.id, msg.message_id)
  
def reset_markup(msg, user):
  bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup = getMarkup(user))
  

    
atexit.register(save_users)
bot.infinity_polling(skip_pending = True)