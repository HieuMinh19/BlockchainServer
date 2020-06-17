from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from core.views import  register, get_last_block, get_signature, test_view


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^register/$', register, name='register_user'),
    url(r'^get-signature', get_signature, name='get_signature'),
    url(r'^test_view', test_view, name='test'),
    url(r'^chain/get-last-block/$', get_last_block, name='chain.last_block'),
]
