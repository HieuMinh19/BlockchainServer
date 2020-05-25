from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from .models import KeyGenerator, BitcoinWallet

def get(self, request, *args, **kwags):
    data = {
        'name': 'Hieu',
        'age': 23
    }
    print(request)
    return JsonResponse(data)

def getData(request):
    data = {
        'name': 'Hieu',
        'age': 23
    }
    if request.method == 'GET':
        data.append({'methods': 'get'})
    elif request.method == 'POST':
        data.append({'methods': 'post'})
        
    return JsonResponse(data)

def test_view(request):
    price_lte = request.GET['price_lte']
    data = {
        'name': 'Hieu',
        'age': 23,
        'price': price_lte
    }
    return JsonResponse(data)

def register(request):
    params = request.GET['random_string']
    generator_class = KeyGenerator()
    generator_class.seed_input(params)
    private_key = generator_class.generate_key()
    wallet = BitcoinWallet()
    public_key = wallet.private_to_public(private_key)
    address = wallet.public_to_address(public_key)
    response = {
        'private_key': private_key,
        'public_key': str(public_key),
        'address': str(address)
    }
    return JsonResponse(response)

