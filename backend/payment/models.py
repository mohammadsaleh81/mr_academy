from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from user.models import User
import random
import string

def generate_random_code(length=36):
    chars =  string.digits
    return ''.join(random.choices(chars, k=length))

class Payment(models.Model):
    GATEWAY_CHOICES = (
        ('zarinpal', 'زرین‌پال'),
    )

    STATUS_CHOICES = (
        ('pending', _('در انتظار پرداخت')),
        ('successful', _('موفق')),
        ('failed', _('ناموفق')),
        ('refunded', _('مسترد شده')),
    )

    gateway = models.CharField(max_length=100, choices=GATEWAY_CHOICES, default='zarinpal')
    pay_local_id = models.CharField(max_length=100, unique=True, editable=False)
    authority = models.CharField(max_length=100, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    done_at = models.DateTimeField(null=True, blank=True)


    card_hash = models.CharField(null=True, blank=True, max_length=100)
    card_pan = models.CharField(null=True, blank=True, max_length=100)
    ref_id = models.CharField(null=True, blank=True, max_length=30)
    fee_type = models.CharField(null=True, blank=True, max_length=30)
    shaparak_fee = models.CharField(null=True, blank=True, max_length=30)


    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_logs', verbose_name=_('user'))
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2)
    ip_address = models.CharField(_('IP address'), blank=True, null=True, max_length=30)
    extra = models.JSONField(blank=True, null=True)



    class Meta:
            ordering = ['-created_at']
            verbose_name = _('Payment')
            verbose_name_plural = _('Payments')


    @classmethod
    def add_pay_id(cls):
        code = generate_random_code(8)
        while cls.objects.filter(pay_local_id=code):
            code = generate_random_code(8)
        return code


    def __str__(self):
        return f"{self.user} of {abs(self.amount)} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


    def save(self, *args, **kwargs):
        if not self.pk:
            self.pay_local_id = self.add_pay_id()
        super().save(*args, **kwargs)






