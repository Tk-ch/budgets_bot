from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import serializers
from rest_framework import status
import dateutil.parser

from ..models import *
from ..serializers import *


@api_view(['POST'])
def add_budget(request):
    budget = BudgetSerializer(data=request.data)
    if budget.is_valid():
        budget.save()
        return Response(budget.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_budgets(request, linkID):
    budget = Budget.objects.get(linkID = linkID)

    if budget: 
        data = BudgetSerializer(budget)
        return Response(data.data)
    else:
        return Response(status = status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def update_budget(request, linkID):
    budget = Budget.objects.get(linkID = linkID)
    data = BudgetSerializer(instance=budget, data=request.data)
  
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_budget(request, linkID):
    budget = get_object_or_404(Budget, linkID=linkID)
    budget.delete()
    return Response(status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def get_balance(request, linkID):
    budget = Budget.objects.get(linkID = linkID)
    data = {'balance': budget.get_balance()}
    return Response(data)

@api_view(['POST'])
def get_sum(request, linkID):
    date=dateutil.parser.parse(request.data['date'])
    budget = Budget.objects.get(linkID = linkID)
    data = {'sum': budget.get_sum(date)}
    return Response(data)