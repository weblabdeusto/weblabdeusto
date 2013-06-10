from django.conf.urls import patterns, url

from weblab_django import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)
