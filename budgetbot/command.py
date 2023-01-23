from cmdFunctions import *
import MessageInfo

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
    Command(['yearly', 'бюджет'], yearly)]