from django.shortcuts import render
from django.http import JsonResponse
import MySQLdb
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser 
from rest_framework.decorators import api_view
from .models import BitcoinWallet, Blockchain, Block, GlobalFunction, TransactionInput, TransactionOutput
import eth_keys, os
import binascii

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
        'private_key': str(private_key)[2:],
        'public_key': str(public_key)[2:],      #convert to string and remove 0x
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

# @api_view(['POST'])
# def get_signature(request):
#     if request.method == "POST":
#         wallet = BitcoinWallet()
#         signature = wallet.generate_signature(request.POST['private_key'], request.POST['msg'])
#         #print('REQUEST', request.post['random_string'])   
#         data = {
#             'code': 200,
#             'data': {
#                 'signature': signature
#             }
#         }
#         #tutorial_data = JSONParser().parse(request)
#         return JsonResponse(data)


def test_view():
    db_ = MySQLdb.connect(host="localhost", port=3306, user="root", passwd="",db="blockchain")
    db_.autocommit(True)
    db_cursor = db_.cursor()
    sql = "SELECT * FROM test_tb"
    result = db_cursor.execute(sql)
    print(result)
    db_.commit() 

@api_view(['POST'])
def create_transaction(request):
    chain = Blockchain()
    globalFunc = GlobalFunction()
    message = request.POST['private_key']
    ## start create data of new block
    print('Message', request.POST['msg'])
    endcodeMsg = request.POST['msg'].encode()
    newBlock = chain.generateNextBlock('I am Hieu Le')
    print('NEW BLOCK', newBlock.hashData)

    keyGenerate = BitcoinWallet()
    privateKey = keyGenerate.recover_private_key(request.POST['private_key'])
    signature = privateKey.sign_msg(request.POST['msg'].encode())
    publicKeyFrom = signature.recover_public_key_from_msg(request.POST['msg'].encode())
   
    allOutput = globalFunc.get_trans_output_by_sign(signature, request.POST['msg'].encode(), request.POST['amount'])
    availableOutput = globalFunc.available_trans_output(request.POST['amount'], allOutput)
    print(availableOutput)
    result = {
        "abc": "thanh cong"
    }

    return JsonResponse(result, safe=False)

