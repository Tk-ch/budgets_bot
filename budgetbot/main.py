import telebot, pickle, atexit
from user import User, users
from conf import API_KEY, DATA
from cmdFunctions import getMarkup
import asyncio

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
  msg = bot.send_message(user.chat, message_info.text, reply_markup=message_info.markup)
  if message_info.delete:
    bot.register_next_step_handler(msg, deleteMessage)
  if message_info.reset_markup:
    if (user.task is not None):
      cancel_task(user)
    task = asyncio.create_task(reset_markup(15, msg, user))
    user.task = task

async def reset_markup(time, msg, user):
  try:
    await asyncio.sleep(time)
    bot.send_message(user.chat, msg.text, reply_markup = getMarkup(user))
    deleteMessage(msg)
  except asyncio.CancelledError:
    pass
  finally:
    user.task = None



def cancel_task(user):
    user.task.cancel()

def deleteMessage(msg):
  bot.delete_message(msg.chat.id, msg.message_id)
  

    
atexit.register(save_users)
bot.infinity_polling(skip_pending = True)