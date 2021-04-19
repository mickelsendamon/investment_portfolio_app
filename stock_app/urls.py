from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('create_stock/', views.create_stock),
    path('new_stock/', views.new_stock),
    path('create_bank/', views.create_bank),
    path('new_bank/', views.new_bank),
    path('create_investment/', views.create_investment),
    path('new_investment/', views.new_investment),
    path('sign_in/', views.sign_in),
    path('log_on/', views.log_on),
    path('logout/', views.logout),
    path('portfolio/', views.portfolio),
    path('stock/<str:ticker>', views.stock),
    path('my_account/', views.my_account),
    path('register/', views.register),
    path('sign_up/', views.sign_up),
]
