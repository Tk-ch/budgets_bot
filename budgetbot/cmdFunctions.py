from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser
import math
from strings import *

markups = {
    'start': ReplyKeyboardMarkup(True, True).row(get_string("mrkp_create_budget"), get_string("mrkp_join_budget")), 
    'none': ReplyKeyboardRemove(), 
    'cancel': ReplyKeyboardMarkup(True, True).add(get_string("mrkp_cancel")), 
    'default': ReplyKeyboardMarkup(True, True).add(get_string("mrkp_add_transaction")).add(get_string("mrkp_balance"), get_string("mrkp_sum"), get_string("mrkp_budget")).add(get_string("mrkp_categories"), get_string("mrkp_purchases"), get_string("mrkp_transactions"), row_width=3).row(get_string("mrkp_add_category"), get_string("mrkp_add_purchase")),
    'manage': ReplyKeyboardMarkup(True, True).row(get_string("mrkp_edit"), get_string("mrkp_delete")).add(get_string("mrkp_cancel"))
}

def noBudget(user):
    user.cmd = {}
    user.questions = []
    return get_string("error_no_budget"), markups['start']

def getMarkup(user):
         if user.budget[0] != '':
             return markups['default']
         return markups['start'] 

def connect(user, message):
    budgetID = message.strip()
    if user.connectBudget(budgetID):
        return get_string("budget_connected", budgetID=budgetID), markups['default']
    return get_string("error_connecting_budget", budgetID=budgetID)

def create(user, message):
    try:
        income = float(message.strip())
        budget = user.createBudget(income)
        if not budget: #if budget not created, inform user
            return get_string("error_creating_budget"), markups['start']
        return get_string("budget_created", budgetID=str(budget)), markups['default']
    except:
        user.command = iter([create])
        return get_string("error_not_a_number"), markups['cancel']
    
def cancel(user, _):
    user.command = None
    user.commandData = {}
    return get_string("action_cancel"), getMarkup(user)

def taxesIncome(user, message):
    try:
        income = float(message)
        user.commandData['income'] = income
        return get_string("action_tax_enter_percent"), markups['cancel']
    except:
        user.command = iter([taxesIncome, taxesCalculate])
        return get_string("error_not_a_number"), markups['cancel']

def taxesCalculate(user, message):
    try:
        taxes = float(message)
        income = user.commandData.pop('income')
        en = income * 0.05 
        esv = 1430
        bank_shit = 50
        tax = en + esv + bank_shit
        money = income - (tax * taxes / 100)
        return get_string("action_tax_output", money=money)
    except: 
        user.command = iter([taxesCalculate])
        return get_string("error_not_a_number"), markups['cancel']

def categoryName(user, message):
    if user.budget[0] == '':
        return noBudget(user)
    user.commandData['name'] = message.strip()
    return get_string("action_category_enter_budget"), markups['cancel']

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
                out = get_string("action_transaction_created_with_category", amount=amount)
            else:
                out = ''
        except:
            out = ''
        return  get_string("action_category_created", name=data['name'], amount=data['amount']) + out, markups['default']
    except:
        user.command = iter([categoryBudget])
        return  get_string("error_not_a_number"), markups['cancel']

def transactionCategory(user, message):
    if user.budget[0] == '':
        return noBudget(user)
    try:
        amount = float(message.strip())
        user.commandData['amount'] = amount
    except: 
        user.command = iter([transactionCategory, transactionCreate])
        return get_string("error_not_a_number"), markups['cancel']
    categories = user.listCategories()
    if not categories: 
        return get_string("error_categories_unavailable"), markups['default']
    markup = ReplyKeyboardMarkup()
    markup.add(get_string("mrkp_create"))
    rows = [category['name'] for category in categories if category['visible']]
    markup.add(*rows, row_width=2)
    markup.add(get_string("mrkp_cancel"))
    return get_string("action_transaction_choose_category"), markup

def transactionCreate(user, message):
    category = message
    if category.lower() == 'создать':
        user.command = iter([categoryName, categoryBudget])
        return get_string("action_category_enter_name"), markups['cancel']
    transaction = user.createTransaction(category, user.commandData.pop('amount'))
    if not transaction: 
        return get_string("error_transaction_not_created"), markups['default']    
    return get_string("action_transaction_created", id=transaction['pk'], amount=transaction['amount']), markups['default']

def purchaseAmount(user, message):
    user.commandData['comment'] = message.strip()
    return get_string("action_purchase_enter_amount"), markups['cancel'] 

def purchaseYear(user, message):
    try: 
        amount = float(message)
        user.commandData['amount'] = amount
        markup = ReplyKeyboardMarkup()
        markup.add('2024', '2025', get_string("mrkp_cancel"), row_width=2)
        return get_string("action_purchase_enter_year"), markup
    except:
        user.command = iter([purchaseYear, purchaseMonth, purchaseCreate])
        return get_string("error_not_a_number"), markups['cancel']

def purchaseMonth(user, message):
    try: 
        year = int(message)
        user.commandData['year'] = year
        markup = ReplyKeyboardMarkup()
        months = [str(i) for i in range(1, 13)]
        markup.add(*months, get_string("mrkp_cancel"), row_width=3)
        return get_string("action_purchase_enter_month"), markup
    except Exception as e:
        print(e)
        user.command = iter([purchaseMonth, purchaseCreate])
        return get_string("error_not_a_number"), markups['cancel']

def purchaseCreate(user, message):
    try: 
        month = int(message)
        try: 
            pk = user.commandData.pop('pk')
            purchase = user.updatePurchase(pk, user.commandData.pop('amount'), user.commandData.pop('comment'), datetime(user.commandData.pop('year'), month, 2))
        except:
            purchase = user.createPurchase(user.commandData.pop('amount'), user.commandData.pop('comment'), datetime(user.commandData.pop('year'), month, 2))
        if not purchase:
            return get_string("error_purchase_not_created"), markups['default']
        return get_string("action_purchase_created"), markups['default']
    except: 
        user.command = iter([purchaseCreate])
        return get_string("error_not_a_number"), markups['cancel']

def balance(user, _):
    if user.budget[0] == '':
        return noBudget(user)
    data = user.getBalance()
    if not data: 
        return get_string("error_balance_not_available"), markups['default']
    return get_string("action_balance_get", balance='{:.2f}'.format(data['balance'])), markups['default']

def getSum(user, _):
    if user.budget[0] == '':
        return noBudget(user)
    today = datetime.now()
    data = user.getSum(today)
    offset = user.getBudget()
    if not data or not offset: 
        return get_string("error_sum_not_available"), markups['default']
    return get_string("action_get_sum") + str(data['sum'] + offset['offset']), markups['default']

def transactions(user, _):
    if user.budget[0] == '':
        return noBudget(user)
    today = datetime.now().replace(tzinfo=None).date()
    first = today.replace(day = 1)
    last = first.replace(month = first.month + 1) 
    data = user.listTransactions(first, last)
    categories = user.listCategories()
    if not data or not categories: 
        return get_string("error_transaction_not_available"), markups['default']

    catnames = {}

    for category in categories:
        catnames[category['pk']] = category['name']
    
    tDates = set([dateutil.parser.parse(t['date']).date() for t in data])

    tDict = {date: [t for t in data if dateutil.parser.parse(t['date']).date() == date] for date in tDates}
    
    out = get_string("action_transaction_list") + '\n'
    for i in sorted(tDict.keys()):
        out += f'{i}:\n'
        for t in tDict[i]: 
            out += f'[{t["pk"]}] {catnames[t["category"]]}: {t["amount"]}\n'
        out += '\n'

    return out, ReplyKeyboardMarkup(True, True).add(get_string("mrkp_cancel"), get_string("mrkp_transaction_delete"), row_width=1)

def categories(user, _):
    today = datetime.now().replace(tzinfo=None).date()
    first = today.replace(day = 1)      
    last = first.replace(month = first.month + 1) 
    data = user.listTransactions(first, last)
    categories = user.listCategories()
    if not data or not categories: 
        return get_string("error_categories_unavailable"), markups['default'] 
        
    catremainders = {}
    
    for transaction in data: 
        if transaction['category'] not in catremainders:
            catremainders[transaction['category']] = 0
        catremainders[transaction['category']] -= transaction['amount']
    
    markup = ReplyKeyboardMarkup(True, True, row_width=2)

    categories = sorted(categories,  key = lambda category: category['amount'], reverse = True)

    catnames = [category['name'] for category in categories if category['visible']]

    out = get_string("action_category_list") + '\n'
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
        out += get_string('action_category_read', name=category['name'], amount = category['amount'], rem = rem, bar = bar)
    markup.add(get_string("mrkp_cancel"))
    markup.add(*catnames, row_width=2)
    return out, markup


def purchases(user, _):
    data = user.listPurchases()
    if not data:
        return get_string("error_purchases_not_available"), markups['default']
    
    markup = ReplyKeyboardMarkup(True, True, row_width=2)

    pDates = set([dateutil.parser.parse(p['date']).date().replace(day=1) for p in data])

    pDict = {date: [p for p in data if dateutil.parser.parse(p['date']).date().replace(day=1) == date] for date in pDates}
    out = get_string("action_purchase_list") + '\n'
    markup.add(get_string("mrkp_cancel"))
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
        return get_string('action_purchase_read', comment = purchase["comment"], amount = purchase["amount"], month = datetime.strftime(dateutil.parser.parse(purchase["date"]).date(), "%Y-%m") ), \
        ReplyKeyboardMarkup().add(get_string("mrkp_perform_purchase")).add(get_string("mrkp_edit"), get_string("mrkp_delete"),get_string("mrkp_cancel"), row_width=2)
    return -1

def purchaseManage(user, message):
    action = message.lower().strip()
    purchase = user.commandData.pop('purchase')
    if action == get_string("mrkp_delete").lower(): 
        user.deleteObject('purchase', purchase)
        return get_string("action_purchase_deleted"), markups['default']
    if action == get_string("mrkp_edit").lower():
        user.commandData['pk'] = purchase
        user.command = iter([purchaseAmount, purchaseYear, purchaseMonth, purchaseCreate])
        return get_string("action_purchase_enter_comment"), markups['cancel']
    if action == get_string("mrkp_perform_purchase").lower():
        user.commandData['pk'] = purchase
        user.command = iter([completePurchase])
        return get_string("action_purchase_enter_actual_amount"), markups['cancel']
    return -1 

def categoryInfo(user, message):
    data = user.listCategories()
    names = [category['name'].lower() for category in data]
    if message.lower() in names:
        #do stuff markups
        category = list(filter(lambda category: (message.lower().strip() in category['name'].lower().strip()), data))[0]
        user.command = iter([categoryManage])
        user.commandData['category'] = category['pk']
        return get_string("action_category_get", name=category['name'], amount=category['amount']), markups['manage']
    return -1

def categoryManage(user, message):
     action = message.lower().strip()
     category = user.commandData.pop('category')
     if action == get_string("mrkp_delete").lower(): 
        user.deleteObject('category', category)
        return get_string("action_category_deleted"), markups['default']
     if action == get_string("mrkp_edit").lower():
        user.commandData['pk'] = category
        user.command = iter([categoryName, categoryBudget])
        return get_string("action_category_enter_name"), markups['cancel']
     return -1

def deleteTransaction(user, message):
    try:
        id = int(message)
        user.deleteObject('transaction', id)
        return get_string("action_transaction_deleted"), markups['default']
    except: 
        return  get_string("error_invalid_id"), markups['cancel']

def completePurchase(user, message):
    try: 
        amount = float(message)
        purchase = user.commandData.pop('pk')
        user.updatePurchaseAmount(purchase, amount)
        user.completePurchase(purchase)
        user.createTransaction('Покупки', amount)
        return get_string("action_purchase_performed", amount=amount)
    except: 
        user.command = iter([completePurchase])
        return 'Не число', markups['cancel']

def yearly(user, _):
    out = ''
    s = user.getBudget()['offset']
    today = datetime.now()
    for i in range(today.month, 13):
        s += user.getSum(today.replace(month = i))["sum"]
        out += get_string("action_get_yearly", i = i, s = s)
    return out