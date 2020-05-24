from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from core.views import test_view, register


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^home/$', test_view, name='TestView'),
    url(r'^register/$', register, name='register_user'),
]
