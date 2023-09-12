from django.urls import path
from .views import post_list, post_detail

app_name = 'blog'  # создание пространства имён приложения

urlpatterns = [
    path('', post_list, name='post_list'),
    path('<int:id>/', post_detail, name='post_detail')
]
