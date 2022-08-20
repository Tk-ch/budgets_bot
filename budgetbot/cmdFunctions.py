from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser
import math

markups = {
    'start': ReplyKeyboardMarkup(True, True).row('Создать бюджет', 'Присоединить'), 
    'none': ReplyKeyboardRemove(), 
    'cancel': ReplyKeyboardMarkup(True, True).add("Отмена"), 
    'default': ReplyKeyboardMarkup(True, True).add('Добавить транзакцию').add("Баланс", "Сумма", "Бюджет").add('Категории', "Покупки", "Транзакции", row_width=3).row('Добавить категорию', 'Добавить покупку'),
    'manage': ReplyKeyboardMarkup(True, True).row('Изменить', 'Удалить').add('Отмена')
}

def noBudget(user):
    user.cmd = {}
    user.questions = []
    return "Сначала нужно создать или присоединить бюджет", markups['start']

def getMarkup(user):
         if user.budget[0] != '':
             return markups['default']
         return markups['start'] 

def connect(user, message):
    budgetID = message.strip()
    if user.connectBudget(budgetID):
        return f'Бюджет {budgetID} успешно присоединен', markups['default']
    return 'Ошибка! Бюджета не существует или @Tkuch что то запорол'

def create(user, message):
    try:
        income = float(message.strip())
        budget = user.createBudget(income)
        if not budget: #if budget not created, inform user
            return "Ошибка - бюджет не создан, пиши этому дибилу @Tkuch", markups['start']
        return "Бюджет создан - ID: " + str(budget), markups['default']
    except:
        user.command = iter([create])
        return "Ошибка - введи число", markups['cancel']
    
def cancel(user, _):
    user.command = None
    user.commandData = {}
    return "Охрана отмена", getMarkup(user)

def taxesIncome(user, message):
    try:
        income = float(message)
        user.commandData['income'] = income
        return "Введи процент нологов", markups['cancel']
    except:
        user.command = iter([taxesIncome, taxesCalculate])
        return "Не число.", markups['cancel']

def taxesCalculate(user, message):
    try:
        taxes = float(message)
        income = user.commandData.pop('income')
        en = income * 0.05 
        esv = 1430
        bank_shit = 50
        tax = en + esv + bank_shit
        money = income - (tax * taxes / 100)
        return f'Твой доход: {money} грн.'
    except: 
        user.command = iter([taxesCalculate])
        return "Не число", markups['cancel']

def categoryName(user, message):
    if user.budget[0] == '':
        return noBudget(user)
    user.commandData['name'] = message.strip()
    return "Теперь введи бюджет", markups['cancel']

def categoryBudget(user, message):
    try: 
        budget = float(message.strip())
        name = user.commandData.pop('name')
        try:
            pk = user.commandData.pop('pk')
            data = user.updateCategory(pk, name, budget)
        except:
            data = user.createCategory(name, budget)
        try: 
            amount = user.commandData.pop('amount')
            transaction = user.createTransaction(data['name'], user.commandData.pop('amount'))
            if transaction:
                out = f'; транзакция на сумму {amount} также создана'
            else:
                out = ''
        except:
            out = ''
        return f"Категория {data['name']} с бюджетом {data['amount']} была создана/отредактирована" + out, markups['default']
    except:
        user.command = iter([categoryBudget])
        return "Не число", markups['cancel']

def transactionCategory(user, message):
    if user.budget[0] == '':
        return noBudget(user)
    try:
        amount = float(message.strip())
        user.commandData['amount'] = amount
    except: 
        user.command = iter([transactionCategory, transactionCreate])
        return "Не число", markups['cancel']
    categories = user.listCategories()
    if not categories: 
        return "Категории недоступны", markups['default']
    markup = ReplyKeyboardMarkup()
    markup.add("Создать")
    rows = [category['name'] for category in categories if category['visible']]
    markup.add(*rows, row_width=2)
    markup.add("Отмена")
    return "Выбери категорию", markup

def transactionCreate(user, message):
    category = message
    if category.lower() == 'создать':
        user.command = iter([categoryName, categoryBudget])
        return "Как называть эту категорию", markups['cancel']
    transaction = user.createTransaction(category, user.commandData.pop('amount'))
    if not transaction: 
        return "Транзакция не создалась :(", markups['default']    
    return f"Транзакция {transaction['pk']} на сумму {transaction['amount']} создана", markups['default']

def purchaseAmount(user, message):
    user.commandData['comment'] = message.strip()
    return "Введи сумму этой вот покупки", markups['cancel'] 

def purchaseYear(user, message):
    try: 
        amount = float(message)
        user.commandData['amount'] = amount
        markup = ReplyKeyboardMarkup()
        markup.add('2022', '2023', 'Отмена', row_width=2)
        return "Введи год покупки", markup
    except:
        user.command = iter([purchaseYear, purchaseMonth, purchaseCreate])
        return "Не число", markups['cancel']

def purchaseMonth(user, message):
    try: 
        year = int(message)
        user.commandData['year'] = year
        markup = ReplyKeyboardMarkup()
        months = [str(i) for i in range(1, 13)]
        markup.add(*months, 'Отмена', row_width=3)
        return 'Введи месяц', markup
    except Exception as e:
        print(e)
        user.command = iter([purchaseMonth, purchaseCreate])
        return "Не число", markups['cancel']

def purchaseCreate(user, message):
    try: 
        month = int(message)
        try: 
            pk = user.commandData.pop('pk')
            purchase = user.updatePurchase(pk, user.commandData.pop('amount'), user.commandData.pop('comment'), datetime(user.commandData.pop('year'), month, 2))
        except:
            purchase = user.createPurchase(user.commandData.pop('amount'), user.commandData.pop('comment'), datetime(user.commandData.pop('year'), month, 2))
        if not purchase:
            return "Непонятные траблы с покупкой", markups['default']
        return "Покупка была создана/отредактирована", markups['default']
    except: 
        user.command = iter([purchaseCreate])
        return 'Да блин не число как так', markups['cancel']

def balance(user, _):
    if user.budget[0] == '':
        return noBudget(user)
    data = user.getBalance()
    if not data: 
        return 'Баланс не доступен, прикол', markups['default']
    return 'Баланс исходя из текущих транзакций: {:.2f}'.format(data['balance']), markups['default']

def getSum(user, _):
    if user.budget[0] == '':
        return noBudget(user)
    today = datetime.now()
    data = user.getSum(today)
    if not data: 
        return 'Остаток не доступен, прикол', markups['default']
    return 'Остаток (прогноз) в этом месяце: ' + str(data['sum']), markups['default']

def transactions(user, _):
    if user.budget[0] == '':
        return noBudget(user)
    today = datetime.now().replace(tzinfo=None).date()
    first = today.replace(day = 1)
    last = first.replace(month = first.month + 1) 
    data = user.listTransactions(first, last)
    categories = user.listCategories()
    if not data or not categories: 
        return 'Транзакции не доступны, прикол', markups['default']

    catnames = {}

    for category in categories:
        catnames[category['pk']] = category['name']
    
    tDates = set([dateutil.parser.parse(t['date']).date() for t in data])

    tDict = {date: [t for t in data if dateutil.parser.parse(t['date']).date() == date] for date in tDates}
    
    out = 'Транзакции:\n'
    for i in sorted(tDict.keys()):
        out += f'{i}:\n'
        for t in tDict[i]: 
            out += f'[{t["pk"]}] {catnames[t["category"]]}: {t["amount"]}\n'
        out += '\n'

    return out, ReplyKeyboardMarkup(True, True).add('Отмена', 'Удалить транзакцию', row_width=1)

def categories(user, _):
    today = datetime.now().replace(tzinfo=None).date()
    first = today.replace(day = 1)      
    last = first.replace(month = first.month + 1) 
    data = user.listTransactions(first, last)
    categories = user.listCategories()
    if not data or not categories: 
        return 'Категории не доступны лол', markups['default'] 
        
    catremainders = {}
    
    for transaction in data: 
        if transaction['category'] not in catremainders:
            catremainders[transaction['category']] = 0
        catremainders[transaction['category']] -= transaction['amount']
    
    markup = ReplyKeyboardMarkup(True, True, row_width=2)

    categories = sorted(categories,  key = lambda category: category['amount'], reverse = True)

    catnames = [category['name'] for category in categories if category['visible']]

    out = 'Категории: \n'
    for category in categories: 
        if not category['visible']:
            continue 
        if category['pk'] in catremainders:
            rem = category['amount'] - catremainders[category['pk']]
        else:
            rem = category['amount']
        if category['amount'] != 0 and rem > 0:
            bar = ''
            bar += '█' * math.floor(rem * 30 / category['amount'])
            bar += '▒' * math.ceil((category['amount'] - rem) * 30 / category['amount'])
            bar += '\n'
        else:
            bar = '▒'*30
            bar+='\n'
        out += f"{category['name']}: Бюджет {category['amount']} / Остаток {rem}\n{bar}"
    markup.add('Отмена')
    markup.add(*catnames, row_width=2)
    return out, markup


def purchases(user, _):
    data = user.listPurchases()
    if not data:
        return "Покупки не доступны", markups['default']
    
    markup = ReplyKeyboardMarkup(True, True, row_width=2)

    pDates = set([dateutil.parser.parse(p['date']).date().replace(day=1) for p in data])

    pDict = {date: [p for p in data if dateutil.parser.parse(p['date']).date().replace(day=1) == date] for date in pDates}
    out = 'Покупки:\n'
    markup.add('Отмена')
    for i in sorted(pDict.keys()):
        out += f'{datetime.strftime(i, "%Y-%m")}:\n'
        for purchase in pDict[i]: 
            out += f"{purchase['comment']} {purchase['amount']} "
            if purchase['done']: 
                out += ' - ✓'
            else: 
                markup.add(purchase['comment']) 
            out += '\n'
        out += '\n'


    
    return out, markup

def purchaseInfo(user, message):
    data = user.listPurchases()
    names = [purchase['comment'].lower() for purchase in data]
    if message.lower() in names:
        #do stuff markups
        purchase = list(filter(lambda purchase: (message.lower().strip() in purchase['comment'].lower().strip()), data))[0]
        user.command = iter([purchaseManage])
        user.commandData['purchase'] = purchase['pk']
        return f'Покупка: {purchase["comment"]}\nСтоимость: {purchase["amount"]}\nМесяц: {datetime.strftime(dateutil.parser.parse(purchase["date"]).date(), "%Y-%m")}', ReplyKeyboardMarkup().add('Совершить покупку').add('Изменить', "Удалить", "Отмена", row_width=2)
    return -1

def purchaseManage(user, message):
    action = message.lower().strip()
    purchase = user.commandData.pop('purchase')
    if action == "удалить": 
        user.deleteObject('purchase', purchase)
        return 'Покупка удалена'
    if action == "изменить":
        user.commandData['pk'] = purchase
        user.command = iter([purchaseAmount, purchaseYear, purchaseMonth, purchaseCreate])
        return "Введи новый комментарий к покупке", markups['cancel']
    if action == "совершить покупку":
        user.commandData['pk'] = purchase
        user.command = iter([completePurchase])
        return "Введи актуальную сумму покупки", markups['cancel']
    return -1 

def categoryInfo(user, message):
    data = user.listCategories()
    names = [category['name'].lower() for category in data]
    if message.lower() in names:
        #do stuff markups
        category = list(filter(lambda category: (message.lower().strip() in category['name'].lower().strip()), data))[0]
        user.command = iter([categoryManage])
        user.commandData['category'] = category['pk']
        return f'Категория {category["name"]}\nСтоимость {category["amount"]}', markups['manage']
    return -1

def categoryManage(user, message):
     action = message.lower().strip()
     category = user.commandData.pop('category')
     if action == "удалить": 
        user.deleteObject('category', category)
        return 'Категория удалена'
     if action == "изменить":
        user.commandData['pk'] = category
        user.command = iter([categoryName, categoryBudget])
        return "Введи новое имя категории", markups['cancel']
     return -1

def deleteTransaction(user, message):
    try:
        id = int(message)
        user.deleteObject('transaction', id)
        return 'Транзакция удалена'
    except: 
        return 'Не айди', markups['cancel']

def completePurchase(user, message):
    try: 
        amount = float(message)
        purchase = user.commandData.pop('pk')
        user.updatePurchaseAmount(purchase, amount)
        user.completePurchase(purchase)
        user.createTransaction('Покупки', amount)
        return 'Покупка совершена, транзакция на сумму ' + str(amount) + ' создана'
    except: 
        user.command = iter([completePurchase])
        return 'Не число', markups['cancel']

def yearly(user, _):
    out = ''
    s = 0
    today = datetime.now()
    for i in range(today.month, 13):
        s += user.getSum(today.replace(month = i))["sum"]
        out += f'Сумма на месяц {i}: {s}\n'
    return out