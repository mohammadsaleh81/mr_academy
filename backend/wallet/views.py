from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, DepositSerializer, WithdrawSerializer

# Create your views here.

class WalletBalanceView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WalletSerializer

    def get_object(self):
        return self.request.user.wallet

class DepositView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepositSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        wallet = request.user.wallet
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Deposit to wallet')

        try:
            wallet.deposit(amount, description=description)
            return Response({'message': 'Deposit successful', 'new_balance': wallet.balance}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WithdrawSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        wallet = request.user.wallet
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', 'Withdrawal from wallet')

        try:
            wallet.withdraw(amount, description=description)
            return Response({'message': 'Withdrawal successful', 'new_balance': wallet.balance}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TransactionHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(wallet=self.request.user.wallet)