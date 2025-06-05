from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from .serializers import PhoneNumberSerializer, OTPVerificationSerializer, UserSerializer
from .services import generate_otp, verify_otp
from wallet.models import ActivityLog
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

User = get_user_model()


class RequestOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            try:
                code = generate_otp(phone_number, request)
                print("=====>>>>>>>>           ", code)  # In production, remove this line
                return Response({
                    'message': _('OTP sent successfully'),
                    'code': code  # In production, remove this line
                }, status=status.HTTP_200_OK)
            except Exception as e:
                # Log the error
                ActivityLog.objects.create(
                    action='verification',
                    status='failure',
                    description=_('Failed to generate OTP'),
                    details={'phone_number': phone_number, 'error': str(e)},
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                return Response({
                    'error': _('Failed to generate OTP. Please try again.')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            
            if verify_otp(phone_number, code, request):
                try:
                    user = User.objects.get(phone_number=phone_number)
                    is_new = False
                    # Update phone verification status
                    if not user.is_phone_verified:
                        user.is_phone_verified = True
                        user.save(update_fields=['is_phone_verified'])
                except User.DoesNotExist:
                    # Create new user with verified phone
                    user = User.objects.create(
                        phone_number=phone_number,
                        is_active=True,
                        is_phone_verified=True
                    )
                    is_new = True

                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Log successful login
                ActivityLog.objects.create(
                    user=user,
                    action='login',
                    status='success',
                    description=_('User logged in successfully'),
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

                return Response({
                    'is_new': is_new,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data,
                }, status=status.HTTP_200_OK)

            return Response({
                'error': _('Invalid or expired OTP')
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Log profile update
            ActivityLog.objects.create(
                user=request.user,
                action='profile_update',
                status='success',
                description=_('User profile updated'),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response({'error': _('No file was submitted.')}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['avatar']

        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if file.content_type not in allowed_types:
            return Response({'error': _('Invalid file type. Only JPEG, PNG, and GIF are allowed.')},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check file size (limit to 5MB)
        if file.size > 5 * 1024 * 1024:
            return Response({'error': _('File size too large. Please keep files under 5MB.')},
                            status=status.HTTP_400_BAD_REQUEST)

        # Delete old avatar if exists
        if request.user.avatar:
            if os.path.isfile(request.user.avatar.path):
                os.remove(request.user.avatar.path)

        filename = f"avatar_{request.user.id}{os.path.splitext(file.name)[1]}"
        path = default_storage.save(f'users/avatars/{filename}', ContentFile(file.read()))
        request.user.avatar = path
        request.user.save()

        # Log avatar update
        ActivityLog.objects.create(
            user=request.user,
            action='avatar_update',
            status='success',
            description=_('User avatar updated'),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        base = "https://api.gport.sbs"
        avatar = request.user.avatar.url if request.user.avatar else '/media/user.png'
        avatar = base + avatar
        return Response({'avatar': avatar}, status=status.HTTP_200_OK)

    def delete(self, request):
        if request.user.avatar:
            if os.path.isfile(request.user.avatar.path):
                os.remove(request.user.avatar.path)
            request.user.avatar = None
            request.user.save()

            # Log avatar deletion
            ActivityLog.objects.create(
                user=request.user,
                action='avatar_delete',
                status='success',
                description=_('User avatar deleted'),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        base = "https://api.gport.sbs"
        avatar = request.user.avatar.url if request.user.avatar else '/media/user.png'
        avatar = base + avatar
        return Response({'avatar': avatar}, status=status.HTTP_200_OK)


    def get(self, request):
        base = "https://api.gport.sbs"
        avatar = request.user.avatar.url if request.user.avatar else '/media/user.png'
        avatar = base + avatar
        return Response({'avatar': avatar})



from django.contrib.auth import logout
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic.base import TemplateView


class logout_page(TemplateView):
    template_name = 'admin/logged_out.html'

    def get(self, request: HttpRequest):
        logout(request)
        return render(request, self.template_name)

    def post(self, request: HttpRequest):
        logout(request)

        return render(request, self.template_name)

