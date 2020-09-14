from django.urls import include, path

from . import views

app_name = "ajax"

urlpatterns = [
    path('', views.index, name='index'),
    path('data/', views.ajax, name='ajax'),
]
