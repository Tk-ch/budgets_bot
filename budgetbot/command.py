from cmdFunctions import *
from MessageInfo import MessageInfo
from strings import *

class Command(): 
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def apply_default_markup(user, message):
        result = Command.parse_message(user, message)
        if result.markup == None:
            markup = get_markup(user)
        return result

    def filter_command(command, message):
        if isinstance(command.name, list):
            return message.lower() in command.name
        return message.lower() == command.name

    def parse_message(user, message):
        command = list(filter(lambda command: Command.filter_command(command, message), commands))
        if len(command) > 0: #command entered in a message
            if isinstance(command[0].func, list): #there's a chain of functions
                user.command = iter(command[0].func)
                return next(user.command)(user, message)
            user.command = None
            user.command_data = {}
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
                user.command = iter([transaction_create])
                user.command_data['amount'] = amount
                categories = user.list_categories()
                if not categories: 
                    return MessageInfo(get_string("error_categories_unavailable"))
                markup = ReplyKeyboardMarkup()
                markup.add(get_string("mrkp_create"))
                rows = [category['name'] for category in categories if category['visible']]
                markup.add(*rows, row_width=2)
                markup.add(get_string("mrkp_cancel"))
                return MessageInfo(get_string('action_transaction_create_from_number'), markup, delete = True)
            except:
                return MessageInfo(get_string("error_invalid_command"))

commands = [
    Command(['start'], lambda *_: MessageInfo(get_string("message_help"))), 
    Command(['create', get_string("mrkp_create_budget").lower()], [
    lambda user, _: MessageInfo(get_string("message_create_budget_already_created"), markups['cancel']) if user.budget != '' else MessageInfo(get_string("message_create_budget"), markups['cancel']),
    create
    ]),
    Command(['connect', get_string("mrkp_join_budget").lower()], [
    lambda user, _: MessageInfo(get_string("message_connect_budget_already_connected"), markups['cancel']) if user.budget[0] != '' else MessageInfo(get_string("message_connect_budget"), markups['cancel']), 
    connect
    ]), 
    Command(['cancel', get_string("mrkp_cancel").lower()], cancel), 
    Command('taxes', 
    [lambda *_: MessageInfo(get_string("message_taxes"), markups['cancel']), 
    taxes_income,
    taxes_calculate]
    ), 
    Command(['category', get_string("mrkp_add_category").lower()],
    [
        lambda *_:MessageInfo(get_string("action_category_enter_name"), markups['cancel'], delete=True, delete_users_message=True),
        category_name, category_budget
    ]
    ), 
    Command(['transaction', get_string("mrkp_add_transaction").lower()], 
    [
        lambda *_: MessageInfo(get_string("message_transaction_amount"), markups['cancel'], delete=True, delete_users_message=True), 
        transaction_category, transaction_create
    ]),
    Command(['purchase', get_string("mrkp_add_purchase").lower()], [
        lambda *_: MessageInfo(get_string("action_purchase_enter_comment"), markups['cancel'], delete=True, delete_users_message=True),
        purchase_amount, purchase_year, purchase_month, purchase_create
    ]), 
    Command(['balance', get_string("mrkp_balance").lower()], balance), 
    Command(['sum', get_string("mrkp_sum").lower()], get_sum), 
    Command(['transactions', get_string("mrkp_transactions").lower()], transactions),
    Command(['categories', get_string("mrkp_categories").lower()], [categories, category_info]),
    Command(['purchases', get_string("mrkp_purchases").lower()], [purchases, purchase_info]),
    Command(['delete', get_string("mrkp_transaction_delete").lower()], [
        lambda *_: MessageInfo(get_string("message_transaction_id"), markups['cancel'], delete=True, delete_users_message=True),
        delete_transaction
        ]
    ), 
    Command(['yearly', get_string("mrkp_budget").lower()], yearly)
    ]