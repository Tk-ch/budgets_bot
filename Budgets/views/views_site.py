from django.http import HttpResponse
from django.template import loader
from ..models import Budget, Transaction, Purchase, Category
from datetime import datetime
from calendar import monthrange

def monthly_view(request, linkID):
    template = loader.get_template('budgets/budgets.html')

    budget = Budget.objects.get(linkID=linkID)

    today = datetime.now().date()
    
    transactions = Transaction.objects.filter(budget = budget, date__gte=today.replace(day=1), date__lte=today.replace(day=monthrange(today.year, today.month)[1]))
    purchases = Purchase.objects.filter(budget = budget, date__gte=today.replace(day=1), date__lte=today.replace(day=3))

    categories = Category.objects.filter(budget=budget).order_by('-amount')

    tDates = sorted(list(set([t.date.date() for t in transactions])))

    tDict = {date: [t for t in transactions if t.date.date() == date] for date in tDates}
   

    purchasesSum = sum([p.amount for p in purchases])
    
    catremainders = {category.name: category.amount for category in categories}

    for transaction in transactions: 
        if transaction.category.name in catremainders:
            catremainders[transaction.category.name] += transaction.amount

    balance = budget.get_balance()

    context = { 
        'budgetIncome': budget.income,
        'transactions': transactions,
        'purchases': purchases,
        'categories': categories,
        'pSum': purchasesSum,
        'tDates': tDates,
        'tDict': tDict,
        'remainders': catremainders,
        'balance': balance
     }


    return HttpResponse(template.render(context, request))

def yearly_view(request, linkID):
    pass