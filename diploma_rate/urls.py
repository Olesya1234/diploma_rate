"""diploma_rate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from core.views import index, login_view, logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^cabinet/commission/', include(('commission_cabinet.urls', 'commission_cabinet'),
                                         namespace='commission_cabinet')),
    url(r'^cabinet/chairman/', include(('chairman_cabinet.urls', 'chairman_cabinet'),
                                         namespace='chairman_cabinet')),
    url(r'^$', index),
    url(r'^login$', login_view),
    url(r'^logout$', logout_view)
]
