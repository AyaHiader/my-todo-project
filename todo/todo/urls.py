# todo/urls.py
from django.contrib import admin
from django.urls import path
from test.views import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api.urls),
]
