from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Restaurant, MenuItem, Order, OrderItem
from .serializers import (
    RestaurantSerializer,
    MenuItemSerializer,
    OrderItemSerializer,
    OrderSerializer,
)


def calculate_order_total(order):
    total = sum(
        item.menu_item.price * item.quantity
        for item in order.items.select_related("menu_item").all()
    )

    order.total = total
    order.save(update_fields=["total"])

    return total


class RestaurantListAPIView(APIView):

    def get(self, request):
        restaurants = Restaurant.objects.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RestaurantSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class RestaurantDetailAPIView(APIView):

    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)

    def put(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)

        serializer = RestaurantSerializer(
            restaurant,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        restaurant.delete()

        return Response(status=204)


class MenuItemListAPIView(APIView):

    def get(self, request):
        menu_items = MenuItem.objects.all()
        serializer = MenuItemSerializer(menu_items, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class MenuItemDetailAPIView(APIView):

    def get(self, request, pk):
        menu_item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemSerializer(menu_item)

        return Response(serializer.data)

    def put(self, request, pk):
        menu_item = get_object_or_404(MenuItem, pk=pk)

        serializer = MenuItemSerializer(
            menu_item,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        menu_item = get_object_or_404(MenuItem, pk=pk)
        menu_item.delete()

        return Response(status=204)


class OrderListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            order = serializer.save(user=request.user)

            return Response(
                OrderSerializer(order).data,
                status=201
            )

        return Response(serializer.errors, status=400)


class OrderDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        serializer = OrderSerializer(order)

        return Response(serializer.data)

    def put(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        serializer = OrderSerializer(
            order,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            user=request.user
        )

        order.delete()

        return Response(status=204)


class OrderItemListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_items = OrderItem.objects.filter(
            order__user=request.user
        )

        serializer = OrderItemSerializer(
            order_items,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = OrderItemSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=400
            )

        order = serializer.validated_data["order"]
        menu_item = serializer.validated_data["menu_item"]
        quantity = serializer.validated_data["quantity"]

        if order.user != request.user:
            return Response(
                {
                    "error": "You cannot add items to this order."
                },
                status=403
            )

     
        if menu_item.restaurant_id != order.restaurant_id:
            return Response(
                {
                    "error": "Menu item does not belong to this restaurant."
                },
                status=400
            )

    
        order_item = OrderItem.objects.filter(
            order=order,
            menu_item=menu_item
        ).first()

        if order_item:

           
            order_item.quantity += quantity
            order_item.save()

        else:

            
            order_item = OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity
            )

     
        calculate_order_total(order)

        return Response(
            OrderItemSerializer(order_item).data,
            status=201
        )


class OrderItemDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        order_item = get_object_or_404(
            OrderItem,
            pk=pk,
            order__user=request.user
        )

        serializer = OrderItemSerializer(order_item)

        return Response(serializer.data)

    def put(self, request, pk):

        order_item = get_object_or_404(
            OrderItem,
            pk=pk,
            order__user=request.user
        )

        serializer = OrderItemSerializer(
            order_item,
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=400
            )

        order = order_item.order
        menu_item = serializer.validated_data["menu_item"]

        if menu_item.restaurant_id != order.restaurant_id:
            return Response(
                {
                    "error": "Menu item does not belong to this restaurant."
                },
                status=400
            )

        order_item = serializer.save()

        calculate_order_total(order)

        return Response(
            OrderItemSerializer(order_item).data
        )

    def delete(self, request, pk):

        order_item = get_object_or_404(
            OrderItem,
            pk=pk,
            order__user=request.user
        )

        order = order_item.order

        order_item.delete()

        calculate_order_total(order)

        return Response(status=204)