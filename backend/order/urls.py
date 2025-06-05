from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    # Order URLs
    path('orders/', views.OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
    path('orders/<int:pk>/refund/', views.OrderRefundView.as_view(), name='order-refund'),
    path('orders/<int:pk>/add-item/', views.OrderAddItemView.as_view(), name='order-add-item'),
    path('orders/<int:pk>/process-payment/', views.OrderProcessPaymentView.as_view(), name='order-process-payment'),

    # OrderItem URLs
    path('order-items/', views.OrderItemListCreateView.as_view(), name='order-item-list'),

    # Payment URLs
    path('payments/', views.PaymentListCreateView.as_view(), name='payment-list'),
    path('payments/<int:pk>/process-wallet/', views.PaymentProcessWalletView.as_view(), name='payment-process-wallet'),
]