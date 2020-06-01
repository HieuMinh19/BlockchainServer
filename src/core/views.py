from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from .models import KeyGenerator, BitcoinWallet, Blockchain

def get(self, request, *args, **kwags):
    data = {
        'name': 'Hieu',
        'age': 23
    }
    print(request)
    return JsonResponse(data)

def register(request):
    #params = request.GET['random_string']
    generator_class = BitcoinWallet()
    private_key = generator_class.generate_private_key()
    public_key = generator_class.generate_public_key(private_key)
    #address = generator_class.public_to_address(public_key)
    response = {
        'private_key': str(private_key),
        'public_key': str(public_key),
        #'address': str(address)
    }
   
    return JsonResponse(response)


def get_last_block(request):
    chain = Blockchain()
    last_block = chain.getLatestBlock()
    print(last_block)
    response = { 
        'index': last_block.index,
        'previousHash': last_block.previousHash,
        'timestamp': last_block.timestamp,
        'transaction': last_block.transaction,
        'hashData': last_block.hashData,
        'nonce': last_block.nonce
    }
    return JsonResponse(response)


    

