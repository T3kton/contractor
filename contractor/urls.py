from django.conf.urls import url
from django.views.generic.base import RedirectView


urlpatterns = [
    url( r'^$', RedirectView.as_view( url='/files/ui/index.html', permanent=True ) ),
    url( r'^favicon.ico$', RedirectView.as_view( url='/files/ui/img/favicon.ico', permanent=True ) ),
]
