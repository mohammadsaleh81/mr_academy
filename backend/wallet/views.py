from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, DepositSerializer, WithdrawSerializer

# Import payment gateway
from payment.gateway.zarinpal import send_payment_request, send_verify
from payment.models import Payment
from django.conf import settings
from datetime import datetime
from django.db import transaction

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

class DepositThroughGatewayView(APIView):
    """Create a payment gateway transaction for wallet deposit"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'مبلغ الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            amount = int(amount)
            if amount < 10000:
                return Response({'error': 'حداقل مبلغ شارژ ۱۰ هزار تومان است'}, status=status.HTTP_400_BAD_REQUEST)
            if amount > 100000000:
                return Response({'error': 'حداکثر مبلغ شارژ ۱۰۰ میلیون تومان است'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'مبلغ نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)

        # Get user details for payment gateway
        user = request.user
        description = f"شارژ کیف پول کاربر {user.get_full_name() or user.phone_number}"
        
        # Create payment record
        payment_instance = Payment()
        
        try:
            # Request payment from gateway
            result = send_payment_request(
                amount=amount,
                description=description,
                email=getattr(user, 'email', ''),
                mobile=getattr(user, 'phone_number', '')
            )
            
            if result.get("data") and result["data"].get("code") == 100:
                authority = result["data"]["authority"]
                payment_url = settings.ZP_API_STARTPAY + authority
                
                # Save payment record
                payment_instance.authority = authority
                payment_instance.user = user
                payment_instance.amount = amount
                payment_instance.ip_address = self.get_client_ip(request)
                payment_instance.extra = {
                    'purpose': 'wallet_deposit',
                    'url': payment_url
                }
                payment_instance.save()
                
                return Response({
                    'success': True,
                    'payment_url': payment_url,
                    'authority': authority,
                    'amount': amount
                })
            else:
                error_message = "خطا در ایجاد درگاه پرداخت"
                if result.get("errors"):
                    error_message = result["errors"].get("message", error_message)
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': f'خطا در اتصال به درگاه پرداخت: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class WalletPaymentVerifyView(APIView):
    """Verify payment and deposit to wallet"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        authority = request.GET.get("Authority")
        pay_status = request.GET.get("Status")
        
        print(f"DEBUG: Payment verification started - Authority: {authority}, Status: {pay_status}")
        
        if not authority:
            return Response({'error': 'پارامتر Authority یافت نشد'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find payment record
        payment_instance = Payment.objects.filter(authority=authority, user=request.user).first()
        
        if not payment_instance:
            print(f"DEBUG: Payment record not found for authority: {authority}")
            return Response({'error': 'رکورد پرداخت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        
        print(f"DEBUG: Payment found - Amount: {payment_instance.amount}, Status: {payment_instance.status}")
        
        # Check if already processed
        if payment_instance.status == 'successful':
            print("DEBUG: Payment already processed")
            return Response({
                'success': True,
                'message': 'این پرداخت قبلاً پردازش شده است',
                'amount': payment_instance.amount,
                'new_balance': request.user.wallet.balance
            })
        
        # If payment was cancelled
        if pay_status != 'OK':
            print(f"DEBUG: Payment cancelled or failed - Status: {pay_status}")
            payment_instance.status = 'failed'
            payment_instance.done_at = datetime.now()
            payment_instance.save()
            return Response({'error': 'پرداخت لغو شد یا با مشکل مواجه شد'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify with gateway
        try:
            print("DEBUG: Sending verification to gateway")
            verify_result = send_verify(
                authority=authority,
                amount=int(payment_instance.amount)
            )
            print(f"DEBUG: Gateway result: {verify_result}")
            
            # Check verification code
            if verify_result.get("data") and verify_result["data"].get("code") in [100, 101]:
                print("DEBUG: Payment verified successfully, adding to wallet")
                
                # Add to wallet
                wallet = request.user.wallet
                try:
                    wallet.deposit(
                        amount=payment_instance.amount,
                        description=f"شارژ کیف پول - کد پیگیری: {payment_instance.pay_local_id}",
                        reference=authority
                    )
                except ValueError as e:
                    if "already exists" in str(e):
                        print("DEBUG: Transaction already exists, payment already processed")
                        return Response({
                            'success': True,
                            'message': 'این پرداخت قبلاً پردازش شده است',
                            'amount': payment_instance.amount,
                            'new_balance': wallet.balance
                        })
                    else:
                        raise e
                
                # Update payment status
                payment_instance.status = 'successful'
                payment_instance.done_at = datetime.now()
                payment_instance.save()
                
                print(f"DEBUG: Success! New balance: {wallet.balance}")
                return Response({
                    'success': True,
                    'message': 'کیف پول با موفقیت شارژ شد',
                    'amount': payment_instance.amount,
                    'new_balance': wallet.balance
                })
            else:
                print(f"DEBUG: Payment verification failed - Code: {verify_result.get('data', {}).get('code')}")
                payment_instance.status = 'failed'
                payment_instance.done_at = datetime.now()
                payment_instance.save()
                return Response({'error': 'تایید پرداخت ناموفق بود'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"DEBUG: Exception during verification: {str(e)}")
            payment_instance.status = 'failed'
            payment_instance.done_at = datetime.now()
            payment_instance.save()
            return Response({'error': f'خطا در تایید پرداخت: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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