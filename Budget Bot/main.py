import telebot, pickle, atexit
from user import User, users

API_KEY = '5596235525:AAEAa7k2bYQhj-JjPt5x58eK0dsYni0gEZw'
bot = telebot.TeleBot(API_KEY)

with open('data.p', 'rb') as fp:
    users = pickle.load(fp)

def exit_handler():
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
    
atexit.register(exit_handler)
bot.infinity_polling(skip_pending = True)



# def parseCommand(user, cmd):
#     #making commands
#     if cmd == '/start':
#         bot.send_message(user.chat, """
#         Привет! Команды тута
#         /create - создаёт бюджет  
#         /connect - соединяет тебя с существующим бюджетом
#         /balance - показывает текущий баланс
#         /sum - рассчитывает остаток в конце месяца (от дохода отнимаются все траты по категориям)
#         /category - добавить категорию
#         /transactions - вывести транзакции
#         /categories - вывести категории и их остатки за месяц
#         /taxes - taxes
#     Для добавления транзакций можно ввести любое число
#     Транзакции следует вводить отрицательными - так проще вводить частые расходы без минуса, а редкие доходы с минусом
#         TODO: 
#         /yearly - годовой прогноз
#         /addpurchase - добавить запланированную покупку
#         /completepurchase - выполнить покупку (создастся транзакция по цене покупки)
#         /removepurchase - удалить покупку
#         """)
#         return user
#     if cmd == '/create': #creating budget
#         if user.state == UserState.CONNECTED: #if budget exists, double-check and set current action to edit-budget
#             bot.send_message(user.chat, "Точно? Один бюджет уже соединен с аккаунтом, он будет утерян. Отправь сумму бюджета, если хочешь продолжить")
#             user.action = Action.EDIT_BUDGET
#             return

#         bot.send_message(user.chat, "Отправь месячный доход")
#         user.action = Action.EDIT_BUDGET
#         return
#     if cmd == '/connect': 
#         bot.send_message(user.chat, "Отправь ID бюджета")
#         user.action = Action.CONNECT_BUDGET
#         return
#     if cmd == '/taxes':
#         bot.send_message(user.chat, """Сколько процентов нологов плотить? 
#         до 471$ - 25%
#         471$ - 718$ - 50%
#         718$ - 1224$ - 75%
#         1224$+ - 100%
#         """)
#         bot.send_message(user.chat, "Введи деняки в гривнах и процент оплаты нологов числами (без знаков кроме точки)")
#         user.action = Action.TAXES
#         return

#     if user.state != UserState.CONNECTED: 
#         bot.send_message(user.chat, "Нужно создать или присоединить бюджет ._.")
#         return
    
#     if cmd == '/category':
#         user.action = Action.ADD_CATEGORY
#         bot.send_message(user.chat, "Введите имя категории и её бюджет через запятую", reply_markup=cancelmarkup)
#         return
#     if cmd == '/balance':
#         user.action = Action.NONE
#         data = user.getBalance()
#         if not data: 
#             bot.send_message(user.chat, 'Баланс не доступен, прикол', reply_markup=ReplyKeyboardRemove())
#             return
#         bot.send_message(user.chat, 'Баланс исходя из текущих транзакций: ' + str(data['balance']))
#         return
#     if cmd == '/sum':
#         user.action = Action.NONE
#         today = datetime.now().replace(tzinfo=None)
#         today += relativedelta(months=1)
#         today = today.replace(day=today.day - 1)
#         data = user.getSum(today)
#         if not data: 
#             bot.send_message(user.chat, 'Остаток не доступен, прикол', reply_markup=ReplyKeyboardRemove())
#             return
#         bot.send_message(user.chat, 'Остаток (прогноз) в этом месяце: ' + str(data['sum']))
#         return
#     if cmd == '/transactions':
#         user.action = Action.NONE
#         today = datetime.now().replace(tzinfo=None).date()
#         first = today.replace(day = 1)
#         last = first.replace(month = first.month + 1) 
#         data = user.listTransactions(first, last)
#         categories = user.listCategories()
#         if not data or not categories: 
#             bot.send_message(user.chat, 'Транзакции не доступны, прикол', reply_markup=ReplyKeyboardRemove())
#             return

#         catnames = {}

#         for category in categories:
#             catnames[category['pk']] = category['name']

#         out = 'Транзакции:\n'
#         for trans in data:
#             out += ''.join([str(dateutil.parser.parse(trans['date']).date()), ': ', str(trans['amount']), ' - ', catnames[trans['category']], '\n'])



#         bot.send_message(user.chat, out)
#         return

#     if cmd == '/categories':
#         user.action = Action.NONE   
#         today = datetime.now().replace(tzinfo=None).date()
#         first = today.replace(day = 1)      
#         last = first.replace(month = first.month + 1) 
#         data = user.listTransactions(first, last)
#         categories = user.listCategories()
#         if not data or not categories: 
#             bot.send_message(user.chat, 'Категории не доступны лол', reply_markup=ReplyKeyboardRemove())
#             return
        
#         catremainders = {}
        
#         for transaction in data: 
#             if transaction['category'] not in catremainders:
#                 catremainders[transaction['category']] = 0
#             catremainders[transaction['category']] -= transaction['amount']
        
#         out = 'Категории: \n'
#         for category in categories: 
#             if not category['visible']:
#                 continue 
#             if category['pk'] in catremainders:
#                 rem = category['amount'] - catremainders[category['pk']]
#             else:
#                 rem = category['amount']
#             if category['amount'] != 0:
#                 bar = ''
#                 bar += '█' * math.floor(rem * 30 / category['amount'])
#                 bar += '▒' * math.ceil((category['amount'] - rem) * 30 / category['amount'])
#                 bar += '\n'
#             else:
#                 bar = ''
#             out += f"{category['name']}: Бюджет {category['amount']} / Остаток {rem}\n{bar}"

#         bot.send_message(user.chat, out)
#         return
        

        

# @bot.message_handler(commands=['start', 'create', 'connect', 'balance', 'sum', 'category', 'transactions', 'categories', 'yearly', 'addpurchase', 'completepurchase', 'removepurchase', 'taxes'])
# def commands(message):
#     text, chat, user = setup(message)
#     user = parseCommand(user, text.split()[0])


# @bot.message_handler()
# def any(message):
#     text, chat, user = setup(message)

#     if user.action == Action.NONE:
#         if user.state != UserState.CONNECTED: 
#             bot.send_message(user.chat, "Не понял :/")
#             return
#         try: 
#             trans = float(text) #if the action is NONE and the user is connected and they sent a number, assume that a transaction is being added
#         except Exception as e: 
#             mylog(repr(e))
#             bot.send_message(user.chat, "Не понимаю")
#         else: 
#             categories = user.listCategories()
#             if not categories:
#                 bot.send_message(user.chat, "Ошибка в получении категорий")
#                 return
#             user.action = Action.CHOOSE_CATEGORY
#             user.trans = trans #saving the transaction for a category
            
#             markup = ReplyKeyboardMarkup(row_width=1)
#             for category in categories:
#                 if category['visible']:
#                     markup.add(KeyboardButton(category['name']))
#             markup.add(KeyboardButton('Создать'))
#             markup.add(KeyboardButton("Отмена"))
#             bot.send_message(user.chat, "Выглядит как транзакция, выбирай категорию: ", reply_markup=markup)
#             return

#     if user.action == Action.TAXES:
#         user.action == None
#         try:
#             income = float(text.split()[0])
#             taxes = float(text.split()[1])
#         except Exception as e:
#             bot.send_message(user.chat, "Что то не то с этими числами")
#             return
#         else: 
#             en = income * 0.05 
#             esv = 1430
#             bank_shit = 50

#             tax = en + esv + bank_shit

#             money = income - (tax * taxes / 100)

#             bot.send_message(user.chat, f"Твой доход {money}")
#             return

#     if user.action == Action.EDIT_BUDGET:
#         try:
#             income = float(text)
#         except Exception as e:
#             mylog(repr(e))
#             bot.send_message(user.chat, "Ошибка - бюджет не создан, введите корректное число")
#             return
#         else:
#             budget = user.createBudget(income)
#             user.action = Action.NONE
#             if not budget: #if budget not created, inform user
#                 bot.send_message(user.chat, "Ошибка - бюджет не создан, пишите этому дибилу @Tkuch")
#                 return
            
#             bot.send_message(user.chat, "Бюджет создан - ID: ")
#             bot.send_message(user.chat, budget)
#             user.state = UserState.CONNECTED
            
#             with open('data.p', 'wb') as fp:
#                 pickle.dump(users, fp, protocol=pickle.HIGHEST_PROTOCOL)
#             return
        
#     if user.action == Action.CONNECT_BUDGET: 
#         if user.connectBudget(text):
#             bot.send_message(user.chat, f'Бюджет {text} успешно присоединен')
#             user.action = Action.NONE
#             user.state = UserState.CONNECTED
#             with open('data.p', 'wb') as fp:
#                 pickle.dump(users, fp, protocol=pickle.HIGHEST_PROTOCOL)
#             return
#         bot.send_message(user.chat, 'Ошибка! Бюджета не существует или @Tkuch что то запорол')
#         return

#     if user.state != UserState.CONNECTED: 
#         bot.send_message(user.chat, "Не понял :/")
#         return

#     if user.action == Action.CHOOSE_CATEGORY:
#         user.action = Action.NONE
#         if text == 'Создать':
#             user.action = Action.ADD_CATEGORY
#             bot.send_message(user.chat, "Введи имя категории и её бюджет через запятую", reply_markup=cancelmarkup)
#             return
#         if text == 'Отмена':
#             user.action = Action.NONE
#             bot.send_message(user.chat, "Понял, значит не транзакция", reply_markup=ReplyKeyboardRemove())
#             return

#         res = user.createTransaction(text, user.trans)
#         if not res: 
#             bot.send_message(user.chat, "Ошибка, транзакция не создана или категория не существует", reply_markup=ReplyKeyboardRemove())
#             return
#         bot.send_message(user.chat, f"Транзакция {res['pk']} на сумму {res['amount']} создана в категории {text}", reply_markup=ReplyKeyboardRemove())
#         return 

#     if user.action == Action.ADD_CATEGORY:
#         if text == 'Отмена':
#             user.action = Action.NONE
#             bot.send_message(user.chat, "Отменяю", reply_markup=ReplyKeyboardRemove())
#             return
#         user.action = Action.NONE
#         category = text.split(',')

#         try: 
#             amount = float(category[1])
#         except Exception as e:
#             mylog(repr(e))
#             bot.send_message(user.chat, "Что то пошло не так", reply_markup=ReplyKeyboardRemove())
#             return

#         data = user.createCategory(category[0].strip(), amount)
#         if not data: 
#             bot.send_message(user.chat, "Категория не создалась :(", reply_markup=ReplyKeyboardRemove())
#             return
        
#         bot.send_message(user.chat, f"Категория {data['name']} с бюджетом {data['amount']} была создана", reply_markup=ReplyKeyboardRemove())

