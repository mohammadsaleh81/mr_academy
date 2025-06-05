from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from user.models import User

# Create your models here.


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet', verbose_name=_('user'))
    balance = models.DecimalField(_('balance'), max_digits=12, decimal_places=2, default=0,
                                  validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('wallet')
        verbose_name_plural = _('wallets')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.phone_number}'s Wallet"

    @transaction.atomic
    def deposit(self, amount, description=None, reference=None):
        """Add funds to wallet balance"""
        if amount <= 0:
            raise ValueError(_("Amount must be positive"))

        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])

        # Create transaction record
        Transaction.objects.create(
            wallet=self,
            amount=amount,
            transaction_type='deposit',
            description=description or _('Deposit to wallet'),
            reference=reference,
            balance_after=self.balance
        )
        return True

    @transaction.atomic
    def withdraw(self, amount, description=None, reference=None):
        """Remove funds from wallet balance"""
        if amount <= 0:
            raise ValueError(_("Amount must be positive"))

        if self.balance < amount:
            raise ValueError(_("Insufficient funds"))

        self.balance -= amount
        self.save(update_fields=['balance', 'updated_at'])

        # Create transaction record
        Transaction.objects.create(
            wallet=self,
            amount=-amount,  # Negative for withdrawal
            transaction_type='withdrawal',
            description=description or _('Withdrawal from wallet'),
            reference=reference,
            balance_after=self.balance
        )
        return True

    @transaction.atomic
    def transfer(self, to_wallet, amount, description=None):
        """Transfer funds to another wallet"""
        if amount <= 0:
            raise ValueError(_("Amount must be positive"))

        if self.balance < amount:
            raise ValueError(_("Insufficient funds"))

        if not isinstance(to_wallet, Wallet):
            raise ValueError(_("Invalid destination wallet"))

        if self.id == to_wallet.id:
            raise ValueError(_("Cannot transfer to the same wallet"))

        # Generate a unique transfer ID to link both transactions
        transfer_id = uuid.uuid4().hex

        # Withdraw from source wallet
        self.withdraw(
            amount=amount,
            description=description or _('Transfer to {}').format(
                to_wallet.user.get_full_name() or to_wallet.user.phone_number),
            reference=transfer_id
        )

        # Deposit to destination wallet
        to_wallet.deposit(
            amount=amount,
            description=description or _('Transfer from {}').format(
                self.user.get_full_name() or self.user.phone_number),
            reference=transfer_id
        )

        return transfer_id


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', _('Deposit')),
        ('withdrawal', _('Withdrawal')),
        ('transfer', _('Transfer')),
        ('payment', _('Payment')),
        ('refund', _('Refund')),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('wallet'))
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(_('balance after'), max_digits=12, decimal_places=2)
    transaction_type = models.CharField(_('transaction type'), max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(_('description'), max_length=255, blank=True)
    reference = models.CharField(_('reference'), max_length=100, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    def __str__(self):
        return f"{self.transaction_type} of {abs(self.amount)} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def is_debit(self):
        return self.amount < 0

    @property
    def is_credit(self):
        return self.amount > 0


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Create a wallet when a new user is created"""
    if created:
        Wallet.objects.create(user=instance)


class TransactionLog(models.Model):
    ACTION_CHOICES = (
        ('deposit', _('Deposit')),
        ('withdrawal', _('Withdrawal')),
        ('transfer_in', _('Transfer In')),
        ('transfer_out', _('Transfer Out')),
        ('payment', _('Payment')),
        ('refund', _('Refund')),
    )

    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transaction_logs',
                               verbose_name=_('wallet'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_logs', verbose_name=_('user'))
    action = models.CharField(_('action'), max_length=20, choices=ACTION_CHOICES)
    amount = models.DecimalField(_('amount'), max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(_('balance before'), max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(_('balance after'), max_digits=12, decimal_places=2)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='completed')
    description = models.CharField(_('description'), max_length=255, blank=True)
    reference = models.CharField(_('reference'), max_length=100, blank=True, null=True, db_index=True)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('transaction log')
        verbose_name_plural = _('transaction logs')

    def __str__(self):
        return f"{self.action} of {abs(self.amount)} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('register', _('Register')),
        ('password_reset', _('Password Reset')),
        ('profile_update', _('Profile Update')),
        ('transaction', _('Transaction')),
        ('verification', _('Verification')),
        ('other', _('Other')),
    )

    STATUS_CHOICES = (
        ('success', _('Success')),
        ('failure', _('Failure')),
        ('warning', _('Warning')),
        ('info', _('Info')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs',
                             verbose_name=_('user'), null=True, blank=True)
    action = models.CharField(_('action'), max_length=20, choices=ACTION_CHOICES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='success')
    description = models.CharField(_('description'), max_length=255, blank=True)
    details = models.JSONField(_('details'), blank=True, null=True)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('activity log')
        verbose_name_plural = _('activity logs')

    def __str__(self):
        user_str = self.user.get_full_name() or self.user.phone_number if self.user else _('Anonymous')
        return f"{user_str} - {self.action} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
