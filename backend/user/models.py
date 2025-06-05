from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), blank=True)
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True)
    otp = models.CharField(_('OTP'), max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_phone_verified = models.BooleanField(_('phone verified'), default=False)
    
    # Profile fields
    bio = models.TextField(_('بیوگرافی'), blank=True, null=True)
    avatar = models.ImageField(_('تصویر پروفایل'), upload_to='users/avatars/', null=True, blank=True)
    birth_date = models.DateField(_('تاریخ تولد'), null=True, blank=True)
    
    # Wallet fields
    wallet_balance = models.DecimalField(
        _('موجودی کیف پول'),
        max_digits=12,
        decimal_places=0,
        null=True,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_spent = models.DecimalField(
        _('مجموع خرید'),
        max_digits=12,
        decimal_places=0,
        default=0,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    # Activity tracking
    last_login_ip = models.GenericIPAddressField(_('آخرین IP ورود'), null=True, blank=True)
    registration_ip = models.GenericIPAddressField(_('IP ثبت‌نام'), null=True, blank=True)
    last_activity = models.DateTimeField(_('آخرین فعالیت'), null=True, blank=True)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})" if self.get_full_name() else self.phone_number

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')

    @property
    def purchased_courses(self):
        """Return all courses purchased by the user"""
        return self.enrollments.select_related('course').all()

    @property
    def active_courses(self):
        """Return courses that the user is currently enrolled in"""
        return self.enrollments.select_related('course').filter(course__is_published=True)

    @property
    def completed_courses(self):
        """Return courses that the user has completed"""
        # This is a placeholder - you'll need to implement course completion tracking
        return []

    @property
    def total_comments(self):
        """Return total number of comments by the user"""
        blog_comments = self.blog_comments.count()
        media_comments = self.media_comments.count()
        return blog_comments + media_comments

    def add_to_wallet(self, amount):
        """Add money to user's wallet"""
        with transaction.atomic():
            self.wallet_balance = models.F('wallet_balance') + amount
            self.save()
            self.refresh_from_db()
        return self.wallet_balance

    def deduct_from_wallet(self, amount):
        """Deduct money from user's wallet"""
        if self.wallet_balance < amount:
            raise ValueError(_('Insufficient funds in wallet'))
        
        with transaction.atomic():
            self.wallet_balance = models.F('wallet_balance') - amount
            self.total_spent = models.F('total_spent') + amount
            self.save()
            self.refresh_from_db()
        return self.wallet_balance

    def update_last_activity(self, ip_address=None):
        """Update user's last activity timestamp and IP"""
        self.last_activity = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=['last_activity', 'last_login_ip'])


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', _('واریز')),
        ('withdraw', _('برداشت')),
        ('purchase', _('خرید')),
        ('refund', _('بازگشت وجه')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    amount = models.DecimalField(_('مبلغ'), max_digits=12, decimal_places=0)
    transaction_type = models.CharField(_('نوع تراکنش'), max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(_('توضیحات'), blank=True)
    created_at = models.DateTimeField(_('تاریخ تراکنش'), auto_now_add=True)
    reference_code = models.UUIDField(_('کد پیگیری'), default=uuid.uuid4, editable=False)
    status = models.CharField(_('وضعیت'), max_length=20, default='completed')

    class Meta:
        verbose_name = _('تراکنش کیف پول')
        verbose_name_plural = _('تراکنش‌های کیف پول')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.phone_number} - {self.amount} - {self.get_transaction_type_display()}"


class OTP(models.Model):
    phone_number = models.CharField(_("شماره تلفن"), max_length=15)
    code = models.CharField(_("کد تایید"), max_length=6)
    created_at = models.DateTimeField(_("زمان ایجاد"), auto_now_add=True)
    expires_at = models.DateTimeField(_("زمان انقضا"))

    def is_valid(self):
        return self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

    class Meta:
        verbose_name = _("کد یکبار مصرف")
        verbose_name_plural = _("کدهای یکبار مصرف")


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Create a wallet transaction record when user's wallet balance changes"""
    if not created and instance.wallet_balance > 0:
        previous_balance = sender.objects.get(pk=instance.pk).wallet_balance
        if instance.wallet_balance != previous_balance:
            amount = instance.wallet_balance - previous_balance
            transaction_type = 'deposit' if amount > 0 else 'withdraw'
            WalletTransaction.objects.create(
                user=instance,
                amount=abs(amount),
                transaction_type=transaction_type,
                description=_('تغییر موجودی کیف پول')
            )

