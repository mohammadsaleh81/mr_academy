from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP, WalletTransaction
import re

User = get_user_model()

class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        # Remove any whitespace
        value = value.strip()
        
        # Check if it matches Iranian phone number format
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("شماره تلفن باید با 09 شروع شود و 11 رقم باشد")
        
        return value

class OTPVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=5)  # Changed to 4 to match OTP generation

    def validate_phone_number(self, value):
        # Remove any whitespace
        value = value.strip()
        
        # Check if it matches Iranian phone number format
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("شماره تلفن باید با 09 شروع شود و 11 رقم باشد")
        
        return value

    def validate_code(self, value):
        # Remove any whitespace
        value = value.strip()
        
        # Check if it's exactly 5 digits
        if not re.match(r'^\d{5}$', value):
            raise serializers.ValidationError("کد تایید باید دقیقا 5 رقم باشد")
        
        return value

class OTPSerializer(serializers.ModelSerializer):
    created_at = serializers.CharField(source='ir_created_at', read_only=True)
    expires_at = serializers.CharField(source='ir_expires_at', read_only=True)
    
    class Meta:
        model = OTP
        fields = ['id', 'phone_number', 'code', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']

class WalletTransactionSerializer(serializers.ModelSerializer):
    created_at = serializers.CharField(source='ir_created_at', read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = ['id', 'user', 'amount', 'transaction_type', 'description', 'created_at', 'reference_code', 'status']
        read_only_fields = ['created_at', 'reference_code']

class UserSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    otp_created_at = serializers.CharField(source='ir_otp_created_at', read_only=True)
    birth_date = serializers.CharField(source='ir_birth_date', read_only=True)
    last_activity = serializers.CharField(source='ir_last_activity', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'email','thumbnail', 'is_phone_verified', 'otp_created_at', 'birth_date', 'last_activity')
        read_only_fields = ('id', 'phone_number', 'is_phone_verified', 'thumbnail', 'otp_created_at', 'birth_date', 'last_activity')


    def get_thumbnail(self, obj):
        path =  obj.avatar.url if obj.avatar else '/media/user.png'
        return  'https://api.gport.sbs' + path