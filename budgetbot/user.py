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
        return Command.apply_default_markup(self, msg)

    def delete_object(self, objectType, pk):
        return api.delete(objectType, pk)

    def create_budget(self, income):
        data = api.create('budget', {'income': income})
        if not data:
            return False
        self.budget[0] = data['linkID']
        self.budget[1] = data['pk']
        return data['linkID']
    
    def connect_budget(self, ID):
        data = api.read('budget', ID)
        if not data: 
            return False
        self.budget[0] = data['linkID']
        self.budget[1] = data['pk']
        return True

    def get_budget(self):
        data = api.read('budget', self.budget[0])
        if not data: 
            return False
        return data


    def list_categories(self, data = {}):
        return api.read('category', self.budget[0], data)

    def create_transaction(self, categoryName, amount): 
        data = api.read('category', self.budget[0], {'name': categoryName})
        if not data: 
            return False
        return api.create('transaction', {'amount': -amount, 'budget': self.budget[1], 'category': data[0]['pk']})
    
    def create_category(self, name, amount):
        return api.create(('category'), {'amount': amount, 'name': name, 'budget': self.budget[1], 'visible': True})
    
    def update_category(self, pk, name, amount):
        return api.update(('category'), pk, {'amount': amount, 'name': name, 'budget': self.budget[1], 'visible': True})
    
    def get_balance(self):
        data = api.request(requests.get, 'budget', 'balance', self.budget[0])
        return data

    def get_sum(self, month):
        data = api.request(requests.post, 'budget', 'sum', self.budget[0], {'date': str(month)})
        return data

    def list_transactions(self, first, last):
        return api.read('transaction', self.budget[0], {'date__gte': str(first), 'date__lt': str(last)})

    def list_purchases(self, data = {}): 
        return api.read('purchase', self.budget[0], data)
        
    def create_purchase(self, amount, comment, date):
        return api.create('purchase', {'amount': amount, 'comment': comment, 'date': str(date), 'budget': self.budget[1]})

    def update_purchase(self, pk, amount, comment, date):
        return api.update('purchase', pk, {'amount': amount, 'comment': comment, 'date': str(date), 'budget': self.budget[1]})
    
    def update_purchase_amount(self, pk, amount):
        return api.update('purchase', pk, {'amount':amount})

    def complete_purchase(self, id):
        data = api.request(requests.get, 'purchase', 'complete', id)
        return data