from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('balance/', views.WalletBalanceView.as_view(), name='balance'),
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('deposit-gateway/', views.DepositThroughGatewayView.as_view(), name='deposit-gateway'),
    path('deposit-verify/', views.WalletPaymentVerifyView.as_view(), name='deposit-verify'),
    path('withdraw/', views.WithdrawView.as_view(), name='withdraw'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='transactions'),
]