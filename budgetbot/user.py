from budgetsAPI import APIHandler as api
from command import Command
import requests

users = {}

class User():
    budget = ['', 0]
    chat = 0
    command = None
    task = None
    commandData = {}
    deletableMessages = []

    def parse(self, msg):
        return Command.applyDefaultMarkup(self, msg)

    def deleteObject(self, objectType, pk):
        return api.delete(objectType, pk)

    def createBudget(self, income):
        data = api.create('budget', {'income': income})
        if not data:
            return False
        self.budget[0] = data['linkID']
        self.budget[1] = data['pk']
        return data['linkID']
    
    def connectBudget(self, ID):
        data = api.read('budget', ID)
        if not data: 
            return False
        self.budget[0] = data['linkID']
        self.budget[1] = data['pk']
        return True

    def getBudget(self):
        data = api.read('budget', self.budget[0])
        if not data: 
            return False
        return data


    def listCategories(self, data = {}):
        return api.read('category', self.budget[0], data)

    def createTransaction(self, categoryName, amount): 
        data = api.read('category', self.budget[0], {'name': categoryName})
        if not data: 
            return False
        return api.create('transaction', {'amount': -amount, 'budget': self.budget[1], 'category': data[0]['pk']})
    
    def createCategory(self, name, amount):
        return api.create(('category'), {'amount': amount, 'name': name, 'budget': self.budget[1], 'visible': True})
    
    def updateCategory(self, pk, name, amount):
        return api.update(('category'), pk, {'amount': amount, 'name': name, 'budget': self.budget[1], 'visible': True})
    
    def getBalance(self):
        data = api.request(requests.get, 'budget', 'balance', self.budget[0])
        return data

    def getSum(self, month):
        data = api.request(requests.post, 'budget', 'sum', self.budget[0], {'date': str(month)})
        return data

    def listTransactions(self, first, last):
        return api.read('transaction', self.budget[0], {'date__gte': str(first), 'date__lt': str(last)})

    def listPurchases(self, data = {}): 
        return api.read('purchase', self.budget[0], data)
        
    def createPurchase(self, amount, comment, date):
        return api.create('purchase', {'amount': amount, 'comment': comment, 'date': str(date), 'budget': self.budget[1]})

    def updatePurchase(self, pk, amount, comment, date):
        return api.update('purchase', pk, {'amount': amount, 'comment': comment, 'date': str(date), 'budget': self.budget[1]})
    
    def updatePurchaseAmount(self, pk, amount):
        return api.update('purchase', pk, {'amount':amount})

    def completePurchase(self, id):
        data = api.request(requests.get, 'purchase', 'complete', id)
        return data