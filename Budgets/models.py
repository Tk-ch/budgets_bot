from django.db import models
from django.utils import timezone
import random, string
from dateutil.relativedelta import relativedelta

class Budget(models.Model): 
    income = models.FloatField()
    linkID = models.CharField(max_length=8, blank=True, unique=True)
    def save(self, *args, **kwargs):
        if (self.pk == None):
            self.linkID = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
            while (Budget.objects.filter(linkID=self.linkID)):
                self.linkID = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
        super(Budget, self).save(*args, **kwargs)
        if Category.objects.filter(budget=self):
            return
        purchases = Category()
        purchases.name = "Покупки"
        purchases.amount = 0
        purchases.budget = self
        purchases.visible = False
        purchases.save()


    def __str__(self):
        return 'Budget ' + self.linkID

    def get_balance(self):
        balance = 0
        transactions = Transaction.objects.filter(budget = self)
        for transaction in transactions:
            balance += transaction.amount
        return balance

    def get_sum(self, date):
        s = 0
        today = timezone.now().replace(day = 1, hour = 1, tzinfo=None)
        date = date.replace(day = 1, hour = 0, minute = 0, second = 0,)
        purchases = Purchase.objects.filter(date__lte=date).filter(date__gte=today)
        while (today <= date): 
            today += relativedelta(months=1)
            s += self.income
            for category in Category.objects.filter(budget=self):
                s -= category.amount

        for purchase in purchases:
            s -= purchase.amount
        
        return s
    
    def get_purchase_category(self):
        return Category.objects.filter(budget=self).get(name="Покупки")
    
    
class Category(models.Model):
    name = models.CharField(max_length=200)
    amount = models.FloatField()
    visible = models.BooleanField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "categories"
    def __str__(self):
        return self.name + ' ' + self.budget.linkID


class Transaction(models.Model):
    date = models.DateTimeField(blank = True, auto_now = True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    amount = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    comment = models.CharField(max_length = 200, blank=True, default='')

    def __str__(self):
        return f'{self.category} - {self.amount} | {self.budget.linkID} | {self.date}'


class Purchase(models.Model): 
    amount = models.FloatField()
    comment = models.CharField(max_length=200)
    date = models.DateTimeField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    def __str__(self):
        return self.comment + ' ' + self.budget.linkID

    def complete(self):
        transaction = Transaction()
        transaction.budget = self.budget
        transaction.category = self.budget.get_purchase_category()
        transaction.amount = self.amount
        transaction.date = timezone.now()
        transaction.comment = self.comment + ' - покупка совершена'
        self.amount = 0
        transaction.save()
        self.save()
        