from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^complete/', views.complete, name='complete'),
    url(r'^auth/', views.auth, name='auth'),
    url(r'^logout/', views.logout_view, name='logout'),
]
