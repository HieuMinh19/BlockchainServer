from django.shortcuts import render
from django.http import JsonResponse

def test_view(request):
    data = {
        'name': 'Hieu',
        'age': 23
    }
    return JsonResponse(data)
