from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('در انتظار پرداخت')),
        ('processing', _('در حال پردازش')),
        ('completed', _('تکمیل شده')),
        ('cancelled', _('لغو شده')),
        ('refunded', _('مسترد شده')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('کاربر'))
    order_number = models.CharField(_('شماره سفارش'), max_length=32, unique=True)
    status = models.CharField(_('وضعیت'), max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(_('مبلغ کل'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    paid_at = models.DateTimeField(_('تاریخ پرداخت'), null=True, blank=True)
    notes = models.TextField(_('یادداشت‌ها'), blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('سفارش')
        verbose_name_plural = _('سفارش‌ها')
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
        ]
        
    def __str__(self):
        return f"سفارش {self.order_number}"

    @classmethod
    def generate_order_number(cls):
        """Generate a unique order number."""
        while True:
            order_number = str(uuid.uuid4().hex)[:8].upper()
            if not cls.objects.filter(order_number=order_number).exists():
                return order_number
    
    @property
    def is_paid(self):
        return self.status in ['completed', 'processing']

    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid."""
        paid_amount = self.payments.filter(status='successful').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return max(0, self.total_amount - paid_amount)

    def can_cancel(self):
        """Check if order can be cancelled."""
        return self.status == 'pending'

    def can_refund(self):
        """Check if order can be refunded."""
        return self.status == 'completed'

    @transaction.atomic
    def mark_as_paid(self):
        """Mark order as paid and trigger necessary actions."""
        if self.remaining_amount > 0:
            raise ValueError(_("Order has remaining unpaid amount"))

        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save()

        # Process each order item
        for item in self.items.all():
            item.process_completion()

    @transaction.atomic
    def cancel(self):
        """Cancel the order and refund any payments."""
        if not self.can_cancel():
            raise ValueError(_("Order cannot be cancelled in its current status"))

        self.status = 'cancelled'
        self.save()

        # Refund any successful payments
        for payment in self.payments.filter(status='successful'):
            payment.refund()

    @transaction.atomic
    def refund(self):
        """Process a refund for the order."""
        if not self.can_refund():
            raise ValueError(_("Order cannot be refunded in its current status"))

        self.status = 'refunded'
        self.save()

        # Process refund for each payment
        for payment in self.payments.filter(status='successful'):
            payment.refund()

class OrderItem(models.Model):
    ITEM_TYPE_CHOICES = (
        ('course', _('دوره')),
        ('other', _('سایر')),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('سفارش'))
    item_type = models.CharField(_('نوع آیتم'), max_length=20, choices=ITEM_TYPE_CHOICES, default='course')
    
    # Direct relation for courses
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='order_items', verbose_name=_('دوره'))
    
    # Generic relation for other content types
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True,
                                   verbose_name=_('نوع محتوا'))
    object_id = models.PositiveIntegerField(_('شناسه محتوا'), null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.DecimalField(_('قیمت'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['id']
        verbose_name = _('آیتم سفارش')
        verbose_name_plural = _('آیتم‌های سفارش')
        indexes = [
            models.Index(fields=['item_type', 'course']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        if self.item_type == 'course':
            return f"{self.quantity}x {self.course.title}"
        return f"{self.quantity}x {self.content_type}"
    
    def clean(self):
        if self.item_type == 'course':
            if not self.course:
                raise ValidationError(_('برای آیتم‌های دوره، انتخاب دوره الزامی است.'))
            if self.content_type or self.object_id:
                raise ValidationError(_('برای آیتم‌های دوره، نباید محتوای عمومی تعریف شود.'))
        else:
            if not (self.content_type and self.object_id):
                raise ValidationError(_('برای آیتم‌های غیر دوره، محتوای عمومی باید تعریف شود.'))
            if self.course:
                raise ValidationError(_('برای آیتم‌های غیر دوره، نباید دوره انتخاب شود.'))
    
    @property
    def total_price(self):
        return self.quantity * self.price

    def get_item(self):
        """Get the actual item this order item refers to."""
        if self.item_type == 'course':
            return self.course
        return self.content_object

    def process_completion(self):
        """Process the completion of this order item."""
        item = self.get_item()
        
        if self.item_type == 'course':
            # Process course enrollment
            from course.models import Enrollment
            Enrollment.objects.get_or_create(
                user=self.order.user,
                course=self.course,
                defaults={
                    'price_paid': self.price,
                    'status': 'active'
                }
            )
        elif hasattr(item, 'process_purchase'):
            # For other items that support purchase processing
            item.process_purchase(self)

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('online', _('پرداخت آنلاین')),
        ('wallet', _('کیف پول')),
        ('bank_transfer', _('انتقال بانکی')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('در انتظار پرداخت')),
        ('successful', _('موفق')),
        ('failed', _('ناموفق')),
        ('refunded', _('مسترد شده')),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name=_('سفارش'))
    amount = models.DecimalField(_('مبلغ'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.CharField(_('روش پرداخت'), max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(_('شناسه تراکنش'), max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(_('وضعیت'), max_length=20, choices=STATUS_CHOICES, default='pending')
    wallet_transaction = models.CharField(_('تراکنش کیف پول'), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    refund_transaction_id = models.CharField(_('شناسه تراکنش استرداد'), max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('پرداخت')
        verbose_name_plural = _('پرداخت‌ها')
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status', 'payment_method']),
        ]
    
    def __str__(self):
        return f"پرداخت {self.transaction_id} برای سفارش {self.order.order_number}"

    @transaction.atomic
    def process_wallet_payment(self):
        """Process payment using user's wallet"""
        if self.payment_method != 'wallet':
            raise ValueError(_("Payment method is not wallet"))
            
        if self.status != 'pending':
            raise ValueError(_("Payment is not in pending status"))
            
        user = self.order.user
        
        try:
            # Try to withdraw from wallet
            reference = f"order_{self.order.order_number}"
            description = _("Payment for order #{order_number}").format(order_number=self.order.order_number)
            
            user.wallet.withdraw(
                amount=self.amount,
                description=description,
                reference=reference
            )
            
            # Update payment status
            self.status = 'successful'
            self.wallet_transaction = reference
            self.save(update_fields=['status', 'wallet_transaction', 'updated_at'])
            
            # Check if order is fully paid and update its status
            if self.order.remaining_amount == 0:
                self.order.mark_as_paid()
            
            return True
        except ValueError as e:
            # In case of insufficient funds or other wallet issues
            self.status = 'failed'
            self.save(update_fields=['status', 'updated_at'])
            return False

    @transaction.atomic
    def refund(self):
        """Process refund for this payment."""
        if self.status != 'successful':
            raise ValueError(_("Only successful payments can be refunded"))

        if self.payment_method == 'wallet':
            # Refund to wallet
            user = self.order.user
            reference = f"refund_order_{self.order.order_number}"
            description = _("Refund for order #{order_number}").format(
                order_number=self.order.order_number
            )
            
            user.wallet.deposit(
                amount=self.amount,
                description=description,
                reference=reference
            )
            
            self.refund_transaction_id = reference
        else:
            # For other payment methods, you might need to integrate with payment gateway
            # This is just a placeholder
            self.refund_transaction_id = f"REFUND_{uuid.uuid4().hex[:8].upper()}"

        self.status = 'refunded'
        self.save()
