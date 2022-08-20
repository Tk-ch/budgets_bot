from cmdFunctions import *

class Command(): 
    def __init__(self, name, func):
        self.name = name
        self.func = func

    

    def applyDefaultMarkup(user, message):
        try:
            result = Command.parseMessage(user, message)
            message, markup = result
        except Exception as e:
            message = result
            markup = getMarkup(user)
        finally:
            return message, markup

    def filterCommand(command, message):
        if isinstance(command.name, list):
            return message.lower() in command.name
        return message.lower() == command.name

    def parseMessage(user, message):
        command = list(filter(lambda command: Command.filterCommand(command, message), commands))
        if len(command) > 0: #command entered in a message
            if isinstance(command[0].func, list): #there's a chain of functions
                user.command = iter(command[0].func)
                return next(user.command)(user, message)
            user.command = None
            user.commandData = {}
            return command[0].func(user, message) #there's only one function
        try: #checking if user has a chain of commands
            command = next(user.command)
            out = command(user, message)
            if out == -1:
                raise Exception()
            return out
        except:
            try:
                amount = float(message)
                user.command = iter([transactionCreate])
                user.commandData['amount'] = amount
                categories = user.listCategories()
                if not categories: 
                    return "Блин, это ж число но категории сдохли", markups['default']
                markup = ReplyKeyboardMarkup()
                markup.add("Создать")
                rows = [category['name'] for category in categories if category['visible']]
                markup.add(*rows, row_width=2)
                markup.add("Отмена")
                return "Выглядит как транзакция, выбери категорию", markup
            except:
                return "Не понял"

commands = [
    Command(['start'], lambda *_: """Привет! Команды тута
         /create - создаёт бюджет  
         /connect - соединяет тебя с существующим бюджетом
         /balance - показывает текущий баланс
         /sum - рассчитывает остаток в конце месяца (от дохода отнимаются все траты по категориям)
         /category - добавить категорию
         /transactions - вывести транзакции
         /categories - вывести категории и их остатки за месяц
         /taxes - taxes
     Для добавления транзакций можно ввести любое число
     Транзакции следует вводить отрицательными - так проще вводить частые расходы без минуса, а редкие доходы с минусом
         TODO: 
         /yearly - годовой прогноз
         /addpurchase - добавить запланированную покупку
         /completepurchase - выполнить покупку (создастся транзакция по цене покупки)
         /removepurchase - удалить покупку"""), 
    Command(['create', 'создать бюджет'], [
    lambda user, _: ("Один бюджет уже подключен. Создание нового бюджета его отключит. Введи сумму если хочешь продолжить", markups['cancel']) if user.budget != '' else ("Введи сумму бюджета", markups['cancel']),
    create
    ]),
    Command(['connect', 'подключить'], [
    lambda user, _: ("Точно? Один бюджет уже подключен. Введи ID:", markups['cancel']) if user.budget[0] != '' else ("Введи ID: ", markups['cancel']), 
    connect
    ]), 
    Command(['cancel', 'отмена'], cancel), 
    Command('taxes', 
    [lambda *_: ("""Сколько процентов нологов плотить? 
#         до 471$ - 25%
#         471$ - 718$ - 50%
#         718$ - 1224$ - 75%
#         1224$+ - 100%
#         ========================
#         Введи доход в гривнах:
#         """, markups['cancel']), 
    taxesIncome,
    taxesCalculate]
    ), 
    Command(['category', 'добавить категорию'],
    [
        lambda *_:("Введи имя категории", markups['cancel']),
        categoryName, categoryBudget
    ]
    ), 
    Command(['transaction', 'добавить транзакцию'], 
    [
        lambda *_: ("Введи количество деняк", markups['cancel']), 
        transactionCategory, transactionCreate
    ]),
    Command(['purchase', 'добавить покупку'], [
        lambda *_: ("Назови свою покупку", markups['cancel']),
        purchaseAmount, purchaseYear, purchaseMonth, purchaseCreate
    ]), 
    Command(['balance', 'баланс'], balance), 
    Command(['sum', "сумма"], getSum), 
    Command(['transactions', "транзакции"], transactions),
    Command(['categories', 'категории'], [categories, categoryInfo]),
    Command(['purchases', 'покупки'], [purchases, purchaseInfo]),
    Command(['delete', 'удалить транзакцию'], [
        lambda *_: ("Введи айдишку кривой транзакции", markups['cancel']),
        deleteTransaction
        ]
    ), 
    Command(['yearly', 'бюджет'], yearly)

]

# class Question():
#     def __init__(self, name, validator, text, errorText):    
#         self.name = name
#         self.text = text
#         self.validator = validator
#         self.errorText = errorText

#     def intValidator(text):
#         try:
#             return int(text)
#         except:
#             return False

#     def floatValidator(text):
#         try: 
#             return float(text)
#         except: 
#             return False

# class Command():
#     def __init__(self, name, replyFunc = None, func = None, questions = []):
#         self.name = name
#         self.replyFunc = replyFunc
#         self.func = func
#         self.questions = questions

#     def getMarkup(user):
#         if user.budget[0] != '':
#             return markups['default']
#         return markups['start'] 

#     def parseMessage(user, msg):
#         if msg.lower() == "отмена" or msg.lower() == 'cancel':
#             user.questions = []
#             user.cmd = {}
#             return 'Охрана отмена', Command.getMarkup(user)
#         if len(user.questions) > 0:  
#             if not user.questions[0].validator(msg): 
#                 return user.questions[0].errorText, Command.getMarkup(user)
#             question = user.questions.pop(0)
#             user.cmd[question.name] = question.validator(msg)
#             if len(user.questions) > 0:
#                 return user.questions[0].text
#         if 'command' in user.cmd:
#             return user.cmd.pop('command').func(user, user.cmd)
#         cmds = list(filter(lambda command: (msg.lower() in command.name), commands))
#         if len(cmds) <= 0:
#             return 'Непонял', Command.getMarkup(user)
         
#         command = cmds[0]
#         if command.func: 
#             user.cmd['command'] = command
#         user.questions = []
#         for question in command.questions:
#             user.questions.append(question)
#         if command.replyFunc:
#             return command.replyFunc(user)
#         if len(command.questions) > 0: 
#             return command.questions[0].text
#         return None

# def createReply(user): 
#     if user.budget[0] != '':
#         return "Точно? Один бюджет уже соединен с аккаунтом, он будет утерян. Отправь сумму бюджета, если хочешь продолжить", markups['cancel']
#     return "Отправь месячный доход", markups['cancel']

# def create(user, data):
#     income = data.pop('income')
#     budget = user.createBudget(income)
#     if not budget: #if budget not created, inform user
#         return "Ошибка - бюджет не создан, пишите этому дибилу @Tkuch", markups['start']
#     return "Бюджет создан - ID: " + str(budget), markups['default']

# def connect(user, data):
#     budgetID = data.pop('budgetID')
#     if user.connectBudget(budgetID):
#         return f'Бюджет {budgetID} успешно присоединен', markups['default']
#     return 'Ошибка! Бюджета не существует или @Tkuch что то запорол', markups['start']

# def taxes(user, data):
#     income = data.pop('income')
#     taxes = data.pop('taxes')
#     en = income * 0.05 
#     esv = 1430
#     bank_shit = 50
#     tax = en + esv + bank_shit
#     money = income - (tax * taxes / 100)
#     return f'Твой доход: {money} грн.', Command.getMarkup(user)

# def noBudget(user):
#     user.cmd = {}
#     user.questions = []
#     return "Сначала нужно создать или присоединить бюджет", markups['start']

# def categoryReply(user):
#     if user.budget[0] == '':
#         return noBudget(user)
#     return "Как называть эту категорию", markups['cancel']

# def category(user, data):
#     category = user.createCategory(data.pop('name'), data.pop('budget'))
#     if not category: 
#         return "Категория не создалась :(", markups['default']    
#     out = ''
#     try:
#         transaction = data.pop('trans_money')
#         t = user.createTransaction(category['name'], transaction)
#         if t:
#             out += '; также, транзакция на сумму ' + str(transaction) + ' была добавлена'
#     except Exception as e:
#         print(e)
#     finally:
#         return f"Категория {category['name']} с бюджетом {category['amount']} была создана" + out, markups['default']

# def transactionReply(user):
#     if user.budget[0] == '':
#         return noBudget(user)
#     categories = user.listCategories()
#     if not categories: 
#         return "Категории недоступны", markups['default'] 
#     markup = ReplyKeyboardMarkup(row_width=2)
#     for category in categories:
#         if category['visible']:
#             markup.add(KeyboardButton(category['name']))
#     markup.add(KeyboardButton("Создать"))
#     markup.add(KeyboardButton("Отмена"))
#     return "Выбери категорию", markup

# def transaction(user, data):
#     category = data.pop('category')
#     if category == 'создать':
#         user.cmd['command'] = commands[4]
#         user.cmd['trans_money'] = data.pop('amount')
#         user.questions = user.cmd['command'].questions
#         return "Как называть эту категорию", markups['cancel']
#     transaction = user.createTransaction(category, data.pop('amount'))
#     if not transaction: 
#         return "Транзакция не создалась :(", markups['default']    
#     return f"Транзакция {transaction['pk']} на сумму {transaction['amount']} создана", markups['default']

# def purchaseReply(user):
#     if user.budget[0] == '':
#         return noBudget(user)
#     return "Назови свою покупку", markups['cancel']

# def purchase(user, data):
#     purchase = user.createPurchase(data.pop('amount'), data.pop('comment'), datetime(data.pop('year'), data.pop('month'), 1))
#     if not purchase:
#         return "Непонятные траблы с покупкой", markups['default']
#     return "Покупка была создана", markups['default']

# def balance(user):
#     if user.budget[0] == '':
#         return noBudget(user)
#     data = user.getBalance()
#     if not data: 
#         return 'Баланс не доступен, прикол', markups['default']
#     return 'Баланс исходя из текущих транзакций: {:.2f}'.format(data['balance']), markups['default']

# def getSum(user):
#     if user.budget[0] == '':
#         return noBudget(user)
#     today = datetime.now().replace(tzinfo=None)
#     today += relativedelta(months=1)
#     today = today.replace(day=today.day - 1)
#     data = user.getSum(today)
#     if not data: 
#         return 'Остаток не доступен, прикол', markups['default']
#     return 'Остаток (прогноз) в этом месяце: ' + str(data['sum']), markups['default']

# def transactions(user):
#     if user.budget[0] == '':
#         return noBudget(user)
#     today = datetime.now().replace(tzinfo=None).date()
#     first = today.replace(day = 1)
#     last = first.replace(month = first.month + 1) 
#     data = user.listTransactions(first, last)
#     categories = user.listCategories()
#     if not data or not categories: 
#         return 'Транзакции не доступны, прикол', markups['default']

#     catnames = {}

#     for category in categories:
#         catnames[category['pk']] = category['name']

#     out = 'Транзакции:\n'
#     for trans in data:
#         out += ''.join(['[', str(trans['pk']), '] ', str(dateutil.parser.parse(trans['date']).date()), ': ', str(trans['amount']), ' - ', catnames[trans['category']], '\n'])

#     return out, ReplyKeyboardMarkup(True, True).add('Удалить транзакцию')

# def categories(user):
#     today = datetime.now().replace(tzinfo=None).date()
#     first = today.replace(day = 1)      
#     last = first.replace(month = first.month + 1) 
#     data = user.listTransactions(first, last)
#     categories = user.listCategories()
#     if not data or not categories: 
#         return 'Категории не доступны лол', markups['default'] 
        
#     catremainders = {}
    
#     for transaction in data: 
#         if transaction['category'] not in catremainders:
#             catremainders[transaction['category']] = 0
#         catremainders[transaction['category']] -= transaction['amount']
    
#     markup = ReplyKeyboardMarkup(True, True, row_width=2)

#     out = 'Категории: \n'
#     for category in categories: 
#         if not category['visible']:
#             continue 
#         if category['pk'] in catremainders:
#             rem = category['amount'] - catremainders[category['pk']]
#         else:
#             rem = category['amount']
#         if category['amount'] != 0 and rem > 0:
#             bar = ''
#             bar += '█' * math.floor(rem * 30 / category['amount'])
#             bar += '▒' * math.ceil((category['amount'] - rem) * 30 / category['amount'])
#             bar += '\n'
#         else:
#             bar = ''
#         out += f"{category['name']}: Бюджет {category['amount']} / Остаток {rem}\n{bar}"
#         markup.add(category['name'])
#     return out, markup

# def categoriesManage(user, data):
#     action = data.pop('action')
#     category = data.pop('category')
#     if action == "удалить": 
#         pass
#     if action == "изменить":
#         pass

#     return Command.parseMessage(user, action)

# def purchases(user):
#     data = user.listPurchases()
#     if not data:
#         return "Покупки не доступны", markups['default']
    
#     markup = ReplyKeyboardMarkup(True, True, row_width=2)
#     out = 'Покупки: \n'
#     for purchase in data:
#         markup.add(purchase['comment'])
#         out += ''.join([purchase['comment'], ' ', str(purchase['amount']), ' ', str(purchase['date']), '\n'])

#     return out, markup



# commands = [
#     Command('start', lambda _ : ("""Привет! Команды тута
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
#         /removepurchase - удалить покупку""", markups['start'])), 
#     Command(('create', 'создать бюджет'), 
#         createReply, 
#         create, 
#         [Question('income', Question.floatValidator, '', 'Число введено неверно')]
#     ), 
#     Command(('connect', 'присоединить'), 
#         lambda _ : ("Отправь ID бюджета", markups['cancel']), 
#         connect, 
#         [Question('budgetID', lambda ID : ID, '', '')]
#     ), 
#     Command('taxes', 
#         lambda _ : ("""Сколько процентов нологов плотить? 
#         до 471$ - 25%
#         471$ - 718$ - 50%
#         718$ - 1224$ - 75%
#         1224$+ - 100%
#         ========================
#         Введи доход в гривнах:
#         """, markups['cancel']),
#         taxes, 
#         [
#             Question('income', Question.floatValidator, '', 'Деньги что-то неправильные'), 
#             Question('taxes', Question.intValidator, ('Введи процент налогов', markups['cancel']), 'Надо целое число пж'), 
#         ]
#     ),
#     Command(('category', "добавить категорию"), 
#         categoryReply,
#         category, 
#         [
#             Question('name', lambda text: text, '', ''), 
#             Question('budget', Question.floatValidator, ('А теперь введи бюджет чиселками:', markups['cancel']), 'Чиселки неправильные :('), 
#         ]
#     ), 
#     Command(('transaction', "добавить транзакцию"), 
#         transactionReply, 
#         transaction, 
#         [
#             Question('category', lambda text: text, '', ''), 
#             Question('amount', Question.floatValidator, ('Введи сумму денег для транзакции', markups['cancel']), "Формат некорректный")
#         ]
#     ), 
#     Command(('purchase', 'добавить покупку'), 
#         purchaseReply, 
#         purchase, 
#         [
#             Question('comment', lambda text: text, '', ''),
#             Question('amount', Question.floatValidator, ('Введи сумму', markups['cancel']), 'Это. Не. Число'), 
#             Question('year', Question.intValidator, ('Введи год', markups['cancel']), 'Какой странный год'), 
#             Question('month', Question.intValidator, ('Введи месяц', markups['cancel']), "Да блин блять")
#         ]
#     ),
#     Command('balance', balance), 
#     Command('sum', getSum),
#     Command('transactions', transactions),
#     Command('categories', categories, categoriesManage, [Question('category', lambda text:text, '', ''), Question('action', lambda text:text, ('Phew', markups['manage']), '')]), 
#     Command('purchases', purchases)
# ]