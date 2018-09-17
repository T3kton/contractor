from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView


urlpatterns = [
    url( r'^$', RedirectView.as_view( url='/files/ui/index.html', permanent=True ) ),
    url( r'^admin/', admin.site.urls ),
    url( r'^favicon.ico$', RedirectView.as_view( url='/files/ui/img/favicon.ico', permanent=True ) ),
]
