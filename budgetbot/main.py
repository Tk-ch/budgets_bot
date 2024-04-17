import telebot, pickle, atexit
from user import User, users
from conf import API_KEY, DATA
from cmdFunctions import get_markup
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

@bot.message_handler(content_types=['text'])
def handle(message):
    text, user = setup(message)
    if (user.task is not None):
        cancel_task(user)
    text = text.lstrip('/')
    msg_info = user.parse(text)
    send_message(user, msg_info)
    if (msg_info.delete_users_message): 
        bot.delete_message(message.chat.id, message.message_id)
    
messages_to_delete = []  

def send_message(user, message_info):
    msg = bot.send_message(user.chat, message_info.text, reply_markup=message_info.markup)
    if message_info.delete:
        messages_to_delete.append(msg)
        bot.register_next_step_handler(msg, delete_message)
    if message_info.reset_markup:
        if (user.task is not None):
            cancel_task(user)
        asyncio.run(reset_task(user, msg))

async def reset_task(user, msg):
  user.task = asyncio.create_task(reset_markup(15, msg, user))
  await user.task

async def reset_markup(time, msg, user):
    try:
        await asyncio.sleep(time)
        message = bot.send_message(user.chat, msg.text, reply_markup = get_markup(user), disable_notification = True)
        delete_message(message)
    except asyncio.CancelledError:
        pass
    finally:
        user.task = None



def cancel_task(user):
    user.task.cancel()

def delete_message():
    for msg in messages_to_delete:
        bot.delete_message(msg.chat.id, msg.message_id)
    messages_to_delete = []
  
atexit.register(save_users)
bot.infinity_polling(skip_pending = True)