from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from core.views import  register, get_last_block


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^register/$', register, name='register_user'),
    url(r'^chain/get-last-block/$', get_last_block, name='chain.last_block'),
]
