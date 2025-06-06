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
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            amount = int(amount)
            if amount < 10000:
                return Response({'error': 'حداقل مبلغ شارژ ۱۰ هزار تومان است'}, status=status.HTTP_400_BAD_REQUEST)
            if amount > 100000000:
                return Response({'error': 'حداکثر مبلغ شارژ ۱۰۰ میلیون تومان است'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)

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
        
        if not authority:
            return Response({'error': 'Authority parameter missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find payment record
            payment_instance = Payment.objects.filter(
                authority=authority,
                user=request.user
            ).first()
            
            if not payment_instance:
                return Response({'error': 'Payment record not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if payment is for wallet deposit
            if payment_instance.extra.get('purpose') != 'wallet_deposit':
                return Response({'error': 'Invalid payment purpose'}, status=status.HTTP_400_BAD_REQUEST)
            
            if pay_status == 'OK':
                # Verify payment with gateway
                try:
                    verify_result = send_verify(
                        authority=authority,
                        amount=int(payment_instance.amount)
                    )
                    
                    # Check if verification was successful
                    if verify_result.get("data") and verify_result["data"].get("code") == 100:
                        # Payment verified successfully, deposit to wallet
                        wallet = request.user.wallet
                        wallet.deposit(
                            amount=payment_instance.amount,
                            description=f"شارژ کیف پول از طریق درگاه - کد پیگیری: {authority}",
                            reference=authority
                        )
                        
                        # Update payment record with verification details
                        payment_instance.status = 'successful'
                        payment_instance.done_at = datetime.now()
                        
                        # Store additional payment details
                        verify_data = verify_result.get("data", {})
                        payment_instance.card_hash = verify_data.get('card_hash', '')
                        payment_instance.card_pan = verify_data.get('card_pan', '')
                        payment_instance.ref_id = verify_data.get('ref_id', '')
                        payment_instance.fee_type = verify_data.get('fee_type', '')
                        payment_instance.shaparak_fee = verify_data.get('shaparak_fee', '')
                        
                        # Update extra field with verification data
                        extra = payment_instance.extra or {}
                        extra.update({'verify': verify_result})
                        payment_instance.extra = extra
                        
                        payment_instance.save()
                        
                        return Response({
                            'success': True,
                            'message': 'کیف پول با موفقیت شارژ شد',
                            'amount': payment_instance.amount,
                            'new_balance': wallet.balance,
                            'ref_id': verify_data.get('ref_id', '')
                        })
                    elif verify_result.get("data") and verify_result["data"].get("code") == 101:
                        # Payment was already verified
                        wallet = request.user.wallet
                        wallet.deposit(
                            amount=payment_instance.amount,
                            description=f"شارژ کیف پول از طریق درگاه - کد پیگیری: {authority}",
                            reference=authority
                        )
                        
                        payment_instance.status = 'successful'
                        payment_instance.done_at = datetime.now()
                        payment_instance.save()
                        
                        return Response({
                            'success': True,
                            'message': 'کیف پول با موفقیت شارژ شد (تراکنش قبلاً تایید شده)',
                            'amount': payment_instance.amount,
                            'new_balance': wallet.balance
                        })
                    else:
                        # Payment verification failed
                        payment_instance.status = 'failed'
                        payment_instance.done_at = datetime.now()
                        payment_instance.save()
                        
                        error_message = "تایید پرداخت از طریق درگاه ناموفق بود"
                        if verify_result.get("errors"):
                            error_message = verify_result["errors"].get("message", error_message)
                        
                        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
                    
                except Exception as e:
                    payment_instance.status = 'failed'
                    payment_instance.done_at = datetime.now()
                    payment_instance.save()
                    return Response({'error': f'خطا در تایید پرداخت: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Payment was cancelled or failed
                payment_instance.status = 'failed'
                payment_instance.done_at = datetime.now()
                payment_instance.save()
                return Response({'error': 'پرداخت لغو شد یا با مشکل مواجه شد'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
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