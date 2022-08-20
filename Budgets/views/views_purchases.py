from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import serializers
from rest_framework import status

from ..models import *
from ..serializers import *

@api_view(['POST'])
def add_purchase(request):
    purchase = PurchaseSerializer(data=request.data)
  
    if Purchase.objects.filter(**request.data).exists():
        raise serializers.ValidationError('This data already exists')
  
    if purchase.is_valid():
        purchase.save()
        return Response(purchase.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_purchases(request, linkID):
    purchases = Purchase.objects.filter(budget__linkID=linkID)

    if purchases: 
        data = PurchaseSerializer(purchases, many = True)
        return Response(data.data)
    else:
        return Response(status = status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def update_purchase(request, pk):
    purchase = Purchase.objects.get(pk = pk)
    data = PurchaseSerializer(instance=purchase, data=request.data, partial = True)
  
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    purchase.delete()
    return Response(status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def complete_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    purchase.complete()
    return Response(status=status.HTTP_202_ACCEPTED)