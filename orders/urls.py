from django.urls import path
from .views import (
    RestaurantListAPIView,
    RestaurantDetailAPIView,
    MenuItemListAPIView,
    MenuItemDetailAPIView,
    OrderItemListAPIView,
    OrderItemDetailAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
)
urlpatterns = [
    path('restaurants/', RestaurantListAPIView.as_view()),
    path('restaurants/<int:pk>/', RestaurantDetailAPIView.as_view()),

    path('menu-items/', MenuItemListAPIView.as_view()),
    path('menu-items/<int:pk>/', MenuItemDetailAPIView.as_view()),

    path('order-items/', OrderItemListAPIView.as_view()),
    path('orders/', OrderListAPIView.as_view()),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view()),
    path('order-items/<int:pk>/', OrderItemDetailAPIView.as_view()),
]