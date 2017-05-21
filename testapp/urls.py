from __future__ import absolute_import

from django.conf.urls import include, url
from django.contrib import admin

from .views import index

admin.autodiscover()

urlpatterns = [
    url(r'^$', index),
    url(r'', include('invoice.urls')),
    url(r'^admin/', include(admin.site.urls))
]
