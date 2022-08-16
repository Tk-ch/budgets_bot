
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

markups = {
    'start': ReplyKeyboardMarkup(True, True).row('Создать бюджет', 'Присоединить'), 
    'none': ReplyKeyboardRemove(), 
    'cancel': ReplyKeyboardMarkup(True, True).add("Отмена"), 
    'default': ReplyKeyboardMarkup(True, True).add('Добавить транзакцию').row('Добавить категорию', 'Добавить покупку'),
    'manage': ReplyKeyboardMarkup(True, True).row('Изменить', 'Удалить').add('Отмена')
}

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
        return "Ошибка - введи число"
    
def cancel(user, _):
    user.command = None
    user.commandData = {}
    return "Охрана отмена", getMarkup(user)

def taxesIncome(user, message):
    try:
        income = float(message)
        user.commandData['income'] = income
        return "Введи процент нологов"
    except:
        user.command = iter([taxesIncome, taxesCalculate])
        return "Не число."

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
        return "Не число"

def categoryName(user, message):
    user.commandData['name'] = message.strip()
    return "Теперь введи бюджет", markups['cancel']

def categoryBudget(user, message):
    try: 
        budget = float(message.strip())
        name = user.commandData.pop('name')
        data = user.createCategory(name, budget)
        return f"Категория {data['name']} с бюджетом {data['amount']} была создана", markups['default']
    except:
        user.command = iter([categoryBudget])
        return "Не число", markups['cancel']

