from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView

class TestView(APIView):
    def get(self, request, *args, **kwags):
        data = {
            'name': 'Hieu',
            'age': 23
        }
        return JsonResponse(data)

# def test_view(request):
#     data = {
#         'name': 'Hieu',
#         'age': 23
#     }
#     return JsonResponse(data)
