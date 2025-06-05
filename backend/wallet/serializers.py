from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = fields

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'description', 'created_at', 'balance_after']
        read_only_fields = fields

class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=255, required=False)

class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=255, required=False)