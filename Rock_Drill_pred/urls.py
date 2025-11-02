from django.urls import path
from . import views

urlpatterns = [
    path('train_model/', views.train_model, name='train_model'),
    path('input/', views.input_page, name='input_page'),
    path('result/', views.result_page, name='result_page'),
]


