from django.conf.urls import url
from converter import views

urlpatterns = [
    url(r'^(?P<amount>\d+(?:\.\d+)?)/(?P<currency_code_1>\w{3})/to/(?P<currency_code_2>\w{3})/in/(?P<response_format>\w+)/$',
        views.request_convert, name='request-convert'),
    url(r'^', views.convert, name='convert')
]
