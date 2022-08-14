from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework import serializers
from rest_framework import status

from ..models import *
from ..serializers import *

@api_view(['POST'])
def add_category(request):
    category = CategorySerializer(data=request.data)
  
    if Category.objects.filter(**request.data).exists():
        raise serializers.ValidationError('This data already exists')
  
    if category.is_valid():
        category.save()
        return Response(category.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_categories(request, linkID):
    categories = Category.objects.filter(budget__linkID=linkID)
    
    if (request.data != None): 
        categories = categories.filter(**request.data)

    if categories: 
        data = CategorySerializer(categories, many = True)
        return Response(data.data)
    else:
        return Response(status = status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def update_category(request, pk):
    category = Category.objects.get(pk = pk)
    data = CategorySerializer(instance=category, data=request.data)
  
    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return Response(status=status.HTTP_202_ACCEPTED)