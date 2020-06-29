from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from core.views import register, get_last_block, test_view
from core.views import create_transaction, get_balance

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^register/$', register, name='register_user'),
    url(r'^transaction/create', create_transaction, name='get_signature'),
    url(r'^test_view', test_view, name='test'),
    url(r'^chain/get-last-block/$', get_last_block, name='chain.last_block'),
    url(r'^balance/$', get_balance, name='get_balance'),
]
