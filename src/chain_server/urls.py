from django.contrib import admin
from django.urls import path
from core.views import test_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', test_view, name='test')
]
