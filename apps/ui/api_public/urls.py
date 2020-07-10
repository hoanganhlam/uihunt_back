from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^uis/$', views.list_ui),
    url(r'^uis/(?P<pk>[-\w]+)/$', views.detail_ui),
    url(r'^fetch-url/$', views.fetch_url),
]
