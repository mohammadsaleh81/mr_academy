from rest_framework import serializers
from .models import Wallet, Transaction, TransactionLog, ActivityLog

class WalletSerializer(serializers.ModelSerializer):
    created_at = serializers.CharField(source='ir_created_at', read_only=True)
    updated_at = serializers.CharField(source='ir_updated_at', read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['balance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = fields

class TransactionSerializer(serializers.ModelSerializer):
    created_at = serializers.CharField(source='ir_created_at', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'description', 'created_at', 'balance_after']
        read_only_fields = fields

class TransactionLogSerializer(serializers.ModelSerializer):
    created_at = serializers.CharField(source='ir_created_at', read_only=True)
    
    class Meta:
        model = TransactionLog
        fields = ['id', 'wallet', 'user', 'action', 'amount', 'balance_before', 'balance_after', 'status', 'description', 'reference', 'ip_address', 'created_at']
        read_only_fields = ['created_at']

class ActivityLogSerializer(serializers.ModelSerializer):
    created_at = serializers.CharField(source='ir_created_at', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'action', 'status', 'description', 'details', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['created_at']

class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=255, required=False)

class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=255, required=False)