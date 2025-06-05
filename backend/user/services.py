# services.py
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import OTP
from wallet.models import ActivityLog
import secrets


def generate_otp(phone_number, request=None):
    """
    Generate a secure OTP for the given phone number
    """
    # Delete any existing OTP for this phone number
    OTP.objects.filter(phone_number=phone_number).delete()

    # Generate a secure 4-digit OTP using secrets module
    code = ''.join(secrets.choice(string.digits) for _ in range(5))

    expires_at = timezone.now() + timedelta(minutes=5)

    otp = OTP.objects.create(
        phone_number=phone_number,
        code=code,
        expires_at=expires_at
    )

    # Log the activity
    if request:
        ActivityLog.objects.create(
            action='verification',
            status='info',
            description=_('OTP sent to phone number'),
            details={'phone_number': phone_number},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

    return code


def verify_otp(phone_number, code, request=None):
    """
    Verify OTP for the given phone number
    """
    try:
        otp = OTP.objects.get(phone_number=phone_number, code=code)
        
        # Check if OTP is valid
        if otp.is_valid():
            # Delete the OTP after successful verification
            otp.delete()
            
            # Log successful verification
            if request:
                ActivityLog.objects.create(
                    action='verification',
                    status='success',
                    description=_('Phone number verified successfully'),
                    details={'phone_number': phone_number},
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            
            return True
        
        # OTP has expired
        otp.delete()
        
        # Log failed verification
        if request:
            ActivityLog.objects.create(
                action='verification',
                status='failure',
                description=_('OTP verification failed - expired code'),
                details={'phone_number': phone_number},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return False
        
    except OTP.DoesNotExist:
        # Log failed verification
        if request:
            ActivityLog.objects.create(
                action='verification',
                status='failure',
                description=_('OTP verification failed - invalid code'),
                details={'phone_number': phone_number},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        return False