# coding: utf-8
from django.conf.urls import url
from invoice.views import download

urlpatterns = [
    url(r'^(?P<uid>[a-zA-Z0-9]+)$', download, name="invoice"),
]
