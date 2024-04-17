from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime
import dateutil.parser
import math
from strings import *
from MessageInfo import MessageInfo

markups = {
    'start': ReplyKeyboardMarkup(True, True).row(get_string("mrkp_create_budget"), get_string("mrkp_join_budget")), 
    'none': ReplyKeyboardRemove(), 
    'cancel': ReplyKeyboardMarkup(True, True).add(get_string("mrkp_cancel")), 
    'default': ReplyKeyboardMarkup(True, True).add(get_string("mrkp_add_transaction")).add(get_string("mrkp_balance"), get_string("mrkp_sum"), get_string("mrkp_budget")).add(get_string("mrkp_categories"), get_string("mrkp_purchases"), get_string("mrkp_transactions"), row_width=3).row(get_string("mrkp_add_category"), get_string("mrkp_add_purchase")),
    'manage': ReplyKeyboardMarkup(True, True).row(get_string("mrkp_edit"), get_string("mrkp_delete")).add(get_string("mrkp_cancel"))
}

def no_budget(user):
    user.cmd = {}
    user.questions = []
    return MessageInfo(get_string("error_no_budget"), markups['start'], delete=True)

def get_markup(user):
    if user.budget[0] != '':
        return markups['default']
    return markups['start'] 

def connect(user, message):
    budgetID = message.strip()
    if user.connect_budget(budgetID):
        return MessageInfo(get_string("budget_connected", budgetID=budgetID), markups['default'])
    return MessageInfo(get_string("error_connecting_budget", budgetID=budgetID), delete=True)

def not_a_number():
    return MessageInfo(get_string("error_not_a_number"), markups['cancel'], delete=True, delete_users_message=True)

def create(user, message):
    try:
        income = float(message.strip())
        budget = user.create_budget(income)
        if not budget: #if budget not created, inform user
            return MessageInfo(get_string("error_creating_budget"), markups['start'])
        return MessageInfo(get_string("budget_created", budgetID=str(budget)), markups['default'], delete_users_message=True)
    except:
        user.command = iter([create])
        return not_a_number()
    
def cancel(user, _):
    user.command = None
    user.command_data = {}
    return MessageInfo(get_string("action_cancel"), get_markup(user), delete=True)

def taxes_income(user, message):
    try:
        income = float(message)
        user.command_data['income'] = income
        return MessageInfo(get_string("action_tax_enter_percent"), markups['cancel'])
    except:
        user.command = iter([taxes_income, taxes_calculate])
        return not_a_number()

def taxes_calculate(user, message):
    try:
        taxes = float(message)
        income = user.command_data.pop('income')
        en = income * 0.05 
        esv = 1430
        bank_shit = 50
        tax = en + esv + bank_shit
        money = income - (tax * taxes / 100)
        return MessageInfo(get_string("action_tax_output", money=money))
    except: 
        user.command = iter([taxes_calculate])
        return not_a_number()

def category_name(user, message):
    if user.budget[0] == '':
        return no_budget(user)
    user.command_data['name'] = message.strip()
    return MessageInfo(get_string("action_category_enter_budget", name=message.strip()), markups['cancel'], delete=True, delete_users_message=True)

def category_budget(user, message):
    try: 
        budget = float(message.strip())
        name = user.command_data.pop('name')
        try:
            pk = user.command_data.pop('pk')
            data = user.update_category(pk, name, budget)
        except:
            data = user.create_category(name, budget)
        try: 
            amount = user.command_data.pop('amount')
            transaction = user.create_transaction(data['name'], user.command_data.pop('amount'))
            if transaction:
                out = get_string("action_transaction_created_with_category", amount=amount)
            else:
                out = ''
        except:
            out = ''
        return  MessageInfo(get_string("action_category_created", name=data['name'], amount=data['amount']) + out, markups['default'], delete_users_message=True)
    except:
        user.command = iter([category_budget])
        return not_a_number()

def transaction_category(user, message):
    if user.budget[0] == '':
        return no_budget(user)
    try:
        amount = float(message.strip())
        user.command_data['amount'] = amount
    except: 
        user.command = iter([transaction_category, transaction_create])
        return not_a_number()
    categories = user.list_categories()
    if not categories: 
        return MessageInfo(get_string("error_categories_unavailable"), markups['default'], delete=True)
    markup = ReplyKeyboardMarkup()
    markup.add(get_string("mrkp_create"))
    rows = [category['name'] for category in categories if category['visible']]
    markup.add(*rows, row_width=2)
    markup.add(get_string("mrkp_cancel"))
    return MessageInfo(get_string("action_transaction_choose_category"), markup, delete=True)

def transaction_create(user, message):
    category = message
    if category.lower() == get_string("mrkp_create").lower():
        user.command = iter([category_name, category_budget])
        return MessageInfo(get_string("action_category_enter_name"), markups['cancel'])
    transaction = user.create_transaction(category, user.command_data.pop('amount'))
    if not transaction: 
        return MessageInfo(get_string("error_transaction_not_created"), markups['default'], delete=True)    
    return MessageInfo(get_string("action_transaction_created", id=transaction['pk'], amount=transaction['amount']), markups['default'], delete_users_message=True)

def purchase_amount(user, message):
    user.command_data['comment'] = message.strip()
    return MessageInfo(get_string("action_purchase_enter_amount"), markups['cancel'], delete=True) 

def purchase_year(user, message):
    try: 
        amount = float(message)
        user.command_data['amount'] = amount
        markup = ReplyKeyboardMarkup()
        markup.add('2024', '2025', get_string("mrkp_cancel"), row_width=2)
        return MessageInfo(get_string("action_purchase_enter_year"), markup, delete=True)
    except:
        user.command = iter([purchase_year, purchase_month, purchase_create])
        return not_a_number()

def purchase_month(user, message):
    try: 
        year = int(message)
        user.command_data['year'] = year
        markup = ReplyKeyboardMarkup()
        months = [str(i) for i in range(1, 13)]
        markup.add(*months, get_string("mrkp_cancel"), row_width=3)
        return MessageInfo(get_string("action_purchase_enter_month"), markup, delete=True)
    except Exception as e:
        print(e)
        user.command = iter([purchase_month, purchase_create])
        return not_a_number()

def purchase_create(user, message):
    try: 
        month = int(message)
        try: 
            pk = user.command_data.pop('pk')
            purchase = user.update_purchase(pk, user.command_data.pop('amount'), user.command_data.pop('comment'), datetime(user.command_data.pop('year'), month, 2))
        except:
            purchase = user.create_purchase(user.command_data.pop('amount'), user.command_data.pop('comment'), datetime(user.command_data.pop('year'), month, 2))
        if not purchase:
            return MessageInfo(get_string("error_purchase_not_created"), markups['default'], delete=True)
        return MessageInfo(get_string("action_purchase_created"), markups['default'], delete_users_message=True)
    except: 
        user.command = iter([purchase_create])
        return not_a_number()

def balance(user, _):
    if user.budget[0] == '':
        return no_budget(user)
    data = user.get_balance()
    if not data: 
        return MessageInfo(get_string("error_balance_not_available"), markups['default'], delete=True, delete_users_message=True)
    return MessageInfo(get_string("action_balance_get", balance='{:.2f}'.format(data['balance'])), markups['default'], delete_users_message=True)

def get_sum(user, _):
    if user.budget[0] == '':
        return no_budget(user)
    today = datetime.now()
    data = user.get_sum(today)
    offset = user.get_budget()
    if not data or not offset: 
        return MessageInfo(get_string("error_sum_not_available"), markups['default'], delete=True,delete_users_message=True)
    return MessageInfo(get_string("action_get_sum") + str(data['sum'] + offset['offset']), markups['default'], delete_users_message=True)

def transactions(user, _):
    if user.budget[0] == '':
        return no_budget(user)
    today = datetime.now().replace(tzinfo=None).date()
    first = today.replace(day = 1)
    last = first.replace(month = first.month + 1) 
    data = user.list_transactions(first, last)
    categories = user.list_categories()
    if not data or not categories: 
        return MessageInfo(get_string("error_transaction_not_available"), markups['default'], delete_users_message=True, delete=True)

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

    return MessageInfo(out, ReplyKeyboardMarkup(True, True).add(get_string("mrkp_cancel"), get_string("mrkp_transaction_delete"), row_width=1), delete_users_message=True)

def categories(user, _):
    today = datetime.now().replace(tzinfo=None).date()
    first = today.replace(day = 1)      
    last = first.replace(month = first.month + 1) 
    data = user.list_transactions(first, last)
    categories = user.list_categories()
    if not data or not categories: 
        return MessageInfo(get_string("error_categories_unavailable"), markups['default'], delete=True, delete_users_message=True) 
        
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
    return MessageInfo(out, markup, delete_users_message=True)


def purchases(user, _):
    data = user.list_purchases()
    if not data:
        return MessageInfo(get_string("error_purchases_not_available"), markups['default'], delete=True, delete_users_message=True)
    
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


    
    return MessageInfo(out, markup, delete_users_message=True)

def purchase_info(user, message):
    data = user.list_purchases()
    names = [purchase['comment'].lower() for purchase in data]
    if message.lower() in names:
        #do stuff markups
        purchase = list(filter(lambda purchase: (message.lower().strip() in purchase['comment'].lower().strip()), data))[0]
        user.command = iter([purchase_manage])
        user.command_data['purchase'] = purchase['pk']
        return MessageInfo(get_string('action_purchase_read', comment = purchase["comment"], amount = purchase["amount"], month = datetime.strftime(dateutil.parser.parse(purchase["date"]).date(), "%Y-%m") ), \
        ReplyKeyboardMarkup().add(get_string("mrkp_perform_purchase")).add(get_string("mrkp_edit"), get_string("mrkp_delete"),get_string("mrkp_cancel"), row_width=2), delete_users_message=True)
    return -1

def purchase_manage(user, message):
    action = message.lower().strip()
    purchase = user.command_data.pop('purchase')
    if action == get_string("mrkp_delete").lower(): 
        user.delete_object('purchase', purchase)
        return MessageInfo(get_string("action_purchase_deleted"), markups['default'], delete_users_message=True)
    if action == get_string("mrkp_edit").lower():
        user.command_data['pk'] = purchase
        user.command = iter([purchase_amount, purchase_year, purchase_month, purchase_create])
        return MessageInfo(get_string("action_purchase_enter_comment"), markups['cancel'], delete_users_message=True)
    if action == get_string("mrkp_perform_purchase").lower():
        user.command_data['pk'] = purchase
        user.command = iter([complete_purchase])
        return MessageInfo(get_string("action_purchase_enter_actual_amount"), markups['cancel'], delete_users_message=True)
    return -1 

def category_info(user, message):
    data = user.list_categories()
    names = [category['name'].lower() for category in data]
    if message.lower() in names:
        #do stuff markups
        category = list(filter(lambda category: (message.lower().strip() in category['name'].lower().strip()), data))[0]
        user.command = iter([category_manage])
        user.command_data['category'] = category['pk']
        return MessageInfo(get_string("action_category_get", name=category['name'], amount=category['amount']), markups['manage'], delete_users_message=True)
    return -1

def category_manage(user, message):
     action = message.lower().strip()
     category = user.command_data.pop('category')
     if action == get_string("mrkp_delete").lower(): 
        user.delete_object('category', category)
        return MessageInfo(get_string("action_category_deleted"), markups['default'], delete_users_message=True)
     if action == get_string("mrkp_edit").lower():
        user.command_data['pk'] = category
        user.command = iter([category_name, category_budget])
        return MessageInfo(get_string("action_category_enter_name"), markups['cancel'], delete_users_message=True)
     return -1

def delete_transaction(user, message):
    try:
        id = int(message)
        user.deleteObject('transaction', id)
        return MessageInfo(get_string("action_transaction_deleted"), markups['default'], delete_users_message=True)
    except: 
        return MessageInfo(get_string("error_invalid_id"), markups['cancel'], delete=True)

def complete_purchase(user, message):
    try: 
        amount = float(message)
        purchase = user.command_data.pop('pk')
        user.update_purchase_amount(purchase, amount)
        user.complete_purchase(purchase)
        user.create_transaction('Покупки', amount)
        return MessageInfo(get_string("action_purchase_performed", amount=amount), delete_users_message=True)
    except: 
        user.command = iter([complete_purchase])
        return not_a_number()

def yearly(user, _):
    out = ''
    s = user.get_budget()['offset']
    today = datetime.now()
    for i in range(today.month, 13):
        s += user.get_sum(today.replace(month = i))["sum"]
        out += get_string("action_get_yearly", i = i, s = s)
    return MessageInfo(out, delete_users_message=True)