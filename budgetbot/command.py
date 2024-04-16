from cmdFunctions import *
from MessageInfo import MessageInfo
from strings import *

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
            return MessageInfo(message, markup, False, True)

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
                    return get_string("error_categories_unavailable"), markups['default']
                markup = ReplyKeyboardMarkup()
                markup.add(get_string("mrkp_create"))
                rows = [category['name'] for category in categories if category['visible']]
                markup.add(*rows, row_width=2)
                markup.add(get_string("mrkp_cancel"))
                return get_string('action_transaction_create_from_number'), markup
            except:
                return get_string("error_invalid_command")

commands = [
    Command(['start'], lambda *_:get_string("message_help")), 
    Command(['create', get_string("mrkp_create_budget").lower()], [
    lambda user, _: (get_string("message_create_budget_already_created"), markups['cancel']) if user.budget != '' else (get_string("message_create_budget"), markups['cancel']),
    create
    ]),
    Command(['connect', get_string("mrkp_join_budget").lower()], [
    lambda user, _: (get_string("message_connect_budget_already_connected"), markups['cancel']) if user.budget[0] != '' else (get_string("message_connect_budget"), markups['cancel']), 
    connect
    ]), 
    Command(['cancel', get_string("mrkp_cancel").lower()], cancel), 
    Command('taxes', 
    [lambda *_: (get_string("message_taxes"), markups['cancel']), 
    taxesIncome,
    taxesCalculate]
    ), 
    Command(['category', get_string("mrkp_add_category").lower()],
    [
        lambda *_:(get_string("action_category_enter_name"), markups['cancel']),
        categoryName, categoryBudget
    ]
    ), 
    Command(['transaction', get_string("mrkp_add_transaction").lower()], 
    [
        lambda *_: (get_string("message_transaction_amount"), markups['cancel']), 
        transactionCategory, transactionCreate
    ]),
    Command(['purchase', get_string("mrkp_add_purchase").lower()], [
        lambda *_: (get_string("action_purchase_enter_comment"), markups['cancel']),
        purchaseAmount, purchaseYear, purchaseMonth, purchaseCreate
    ]), 
    Command(['balance', get_string("mrkp_balance").lower()], balance), 
    Command(['sum', get_string("mrkp_sum").lower()], getSum), 
    Command(['transactions', get_string("mrkp_transactions").lower()], transactions),
    Command(['categories', get_string("mrkp_categories").lower()], [categories, categoryInfo]),
    Command(['purchases', get_string("mrkp_purchases").lower()], [purchases, purchaseInfo]),
    Command(['delete', get_string("mrkp_transaction_delete").lower()], [
        lambda *_: (get_string("message_transaction_id"), markups['cancel']),
        deleteTransaction
        ]
    ), 
    Command(['yearly', get_string("mrkp_budget").lower()], yearly)]