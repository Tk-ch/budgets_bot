from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import serializers
from rest_framework import status

from ..models import *
from ..serializers import *

@api_view(['POST'])
def add_transaction(request):
    transaction = TransactionSerializer(data=request.data)
  
  
    if transaction.is_valid():
        transaction.save()
        return Response(transaction.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_transactions(request, linkID):
    transactions = Transaction.objects.filter(budget__linkID=linkID)

    if (request.data != None): 
        transactions = transactions.filter(**request.data)

    if transactions: 
        data = TransactionSerializer(transactions, many = True)
        return Response(data.data)
    else:
        return Response(status = status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def update_transaction(request, pk):
    transaction = Transaction.objects.get(pk = pk)
    data = TransactionSerializer(instance=transaction, data=request.data)
  
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.delete()
    return Response(status=status.HTTP_202_ACCEPTED)