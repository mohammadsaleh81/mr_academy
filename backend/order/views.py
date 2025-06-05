from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
import uuid
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Order, OrderItem, Payment
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    PaymentSerializer, PaymentCreateSerializer, OrderItemSerializer
)
from .filters import OrderFilter
from rest_framework.views import APIView


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order if it's in a cancellable state."""
        order = self.get_object()
        
        try:
            order.cancel()
            return Response(
                {'message': _('Order cancelled successfully')},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Request a refund for an order."""
        order = self.get_object()
        
        try:
            order.refund()
            return Response(
                {'message': _('Refund processed successfully')},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {"detail": "Can only add items to pending orders"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            # Update order total
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {"detail": "Order is not in pending status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            payment_data = {
                'order': order,
                'amount': order.total_amount,
                'payment_method': request.data.get('payment_method', 'online'),
                'transaction_id': str(uuid.uuid4().hex),
                'status': 'pending'
            }
            
            payment = Payment.objects.create(**payment_data)
            
            # Here you would integrate with your payment gateway
            # For demonstration, we'll assume payment is successful
            payment.status = 'successful'
            payment.save()
            
            # Update order status
            order.status = 'completed'
            order.paid_at = timezone.now()
            order.save()
            
            return Response({
                'detail': 'Payment processed successfully',
                'payment': PaymentSerializer(payment).data
            })

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)
    
    def perform_create(self, serializer):
        order_id = self.request.data.get('order')
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        serializer.save(order=order)

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def process_wallet_payment(self, request, pk=None):
        """Process a wallet payment."""
        payment = self.get_object()
        
        if payment.payment_method != 'wallet':
            return Response(
                {'error': _('This payment is not a wallet payment')},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if payment.status != 'pending':
            return Response(
                {'error': _('This payment cannot be processed')},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        success = payment.process_wallet_payment()
        
        if success:
            return Response(
                {'message': _('Payment processed successfully')},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': _('Payment processing failed')},
                status=status.HTTP_400_BAD_REQUEST
            )

class OrderListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        # Apply filters, search, and ordering
        for backend in self.filter_backends:
            orders = backend().filter_queryset(request, orders, self)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Order, pk=pk, user=self.request.user)

    def get(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderDetailSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        try:
            order.cancel()
            return Response({'message': _('Order cancelled successfully')}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderRefundView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        try:
            order.refund()
            return Response({'message': _('Refund processed successfully')}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderAddItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status != 'pending':
            return Response({"detail": "Can only add items to pending orders"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderProcessPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status != 'pending':
            return Response({"detail": "Order is not in pending status"}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            payment_data = {
                'order': order,
                'amount': order.total_amount,
                'payment_method': request.data.get('payment_method', 'online'),
                'transaction_id': str(uuid.uuid4().hex),
                'status': 'pending'
            }
            
            payment = Payment.objects.create(**payment_data)
            
            # Here you would integrate with your payment gateway
            # For demonstration, we'll assume payment is successful
            payment.status = 'successful'
            payment.save()
            
            order.status = 'completed'
            order.paid_at = timezone.now()
            order.save()
            
            return Response({
                'detail': 'Payment processed successfully',
                'payment': PaymentSerializer(payment).data
            })

class OrderItemListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        order_items = OrderItem.objects.filter(order__user=request.user)
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            order_id = request.data.get('order')
            order = get_object_or_404(Order, id=order_id, user=request.user)
            serializer.save(order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']

    def get(self, request):
        payments = Payment.objects.filter(order__user=request.user)
        # Apply filters and ordering
        for backend in self.filter_backends:
            payments = backend().filter_queryset(request, payments, self)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentProcessWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, order__user=request.user)
        
        if payment.payment_method != 'wallet':
            return Response({'error': _('This payment is not a wallet payment')}, status=status.HTTP_400_BAD_REQUEST)
            
        if payment.status != 'pending':
            return Response({'error': _('This payment cannot be processed')}, status=status.HTTP_400_BAD_REQUEST)
            
        success = payment.process_wallet_payment()
        
        if success:
            return Response({'message': _('Payment processed successfully')}, status=status.HTTP_200_OK)
        else:
            return Response({'error': _('Payment processing failed')}, status=status.HTTP_400_BAD_REQUEST)
