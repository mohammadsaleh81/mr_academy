from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP
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
        
        # Check if it's exactly 4 digits
        if not re.match(r'^\d{5}$', value):
            raise serializers.ValidationError("کد تایید باید دقیقا 4 رقم باشد")
        
        return value

class UserSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'email','thumbnail', 'is_phone_verified')
        read_only_fields = ('id', 'phone_number', 'is_phone_verified', 'thumbnail')


    def get_thumbnail(self, obj):
        path =  obj.avatar.url if obj.avatar else '/media/user.png'
        return  'https://api.gport.sbs' + path