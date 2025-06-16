from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_form, name='order_form'),
    path('order/<int:order_id>/confirm/', views.confirm_order, name='confirm_order'),
]