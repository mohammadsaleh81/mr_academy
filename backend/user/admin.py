from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django import forms
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from wallet.models import User, Wallet, Transaction, TransactionLog, ActivityLog
from user.models import WalletTransaction


class ManualTransactionForm(forms.Form):
    amount = forms.DecimalField(
        label=_('مبلغ'),
        min_value=0,
        decimal_places=0,
        help_text=_('مبلغ به تومان')
    )
    description = forms.CharField(
        label=_('توضیحات'),
        max_length=255,
        required=False,
        help_text=_('توضیحات تراکنش')
    )


class WalletTransactionInline(TabularInline):
    model = WalletTransaction
    extra = 0
    fields = ('amount', 'transaction_type', 'description', 'reference_code', 'status', 'created_at')
    readonly_fields = ('amount', 'transaction_type', 'description', 'reference_code', 'status', 'created_at')
    can_delete = False
    max_num = 10
    show_change_link = True
    
    # Unfold customizations
    tab = True
    tab_title = _("تراکنش‌های اخیر")

    verbose_name = _("تراکنش")
    verbose_name_plural = _("تراکنش‌های اخیر")
    classes = ('collapse-entry',)
    
    def has_add_permission(self, request, obj=None):
        return False


class WalletInline(TabularInline):
    model = Wallet
    fields = ('balance', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('balance', 'created_at', 'updated_at')
    can_delete = False
    max_num = 1
    min_num = 1
    show_change_link = True
    
    # Unfold customizations
    tab = True
    tab_title = _("Wallet")
    # tab_icon = "account_balance_wallet"
    verbose_name = _("Wallet")
    verbose_name_plural = _("Wallet")
    classes = ('collapse-entry',)


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_display = ('phone_number', 'get_full_name', 'wallet_balance', 'total_spent', 
                   'is_active', 'is_staff', 'is_phone_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_phone_verified')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    inlines = [WalletTransactionInline]

    # Unfold customizations
    icon = "person"
    search_help_text = "جستجو بر اساس شماره تلفن، نام یا ایمیل"
    date_hierarchy = 'date_joined'
    show_full_result_count = True
    save_on_top = True
    
    fieldsets = (
        (None, {
            'fields': ('phone_number', 'password'),
            'classes': ('tab',),
            # 'tab_icon': 'phone'
        }),
        (_('اطلاعات شخصی'), {
            'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar', 'birth_date'),
            'classes': ('tab',),
            # 'tab_icon': 'person'
        }),
        (_('کیف پول'), {
            'fields': ('wallet_balance', 'total_spent'),
            'classes': ('tab',),
            # 'tab_icon': 'account_balance_wallet'
        }),
        (_('تایید شماره تلفن'), {
            'fields': ('is_phone_verified', 'otp', 'otp_created_at'),
            'classes': ('tab',),
            # 'tab_icon': 'verified_user'
        }),
        (_('دسترسی‌ها'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('tab',),
            # 'tab_icon': 'security'
        }),
        (_('فعالیت‌ها'), {
            'fields': ('last_login', 'date_joined', 'last_activity', 'last_login_ip', 'registration_ip'),
            'classes': ('tab',),
            # 'tab_icon': 'history'
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )

    def wallet_balance(self, obj):
        return f"{obj.wallet_balance:,} تومان"
    wallet_balance.short_description = _('موجودی کیف پول')
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.phone_number
    get_full_name.short_description = _('نام کامل')


@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    list_display = ('id', 'user_link', 'balance', 'is_active', 'transaction_count', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('balance', 'created_at', 'updated_at', 'user_link')
    actions = ['activate_wallets', 'deactivate_wallets']
    
    # Unfold customizations
    icon = "account_balance_wallet"
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Wallet Information'), {
            'fields': ('user_link', 'balance', 'is_active'),
            'classes': ('tab',),
            # 'tab_icon': 'info'
        }),
        (_('Manual Operations'), {
            'fields': ('manual_deposit_form', 'manual_withdraw_form'),
            'classes': ('tab',),
            # 'tab_icon': 'edit'
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
            # 'tab_icon': 'schedule'
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')
        return queryset
    
    def user_link(self, obj):
        url = reverse("admin:user_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.phone_number)
    user_link.short_description = _('User')
    
    def transaction_count(self, obj):
        return obj.transactions.count()
    transaction_count.short_description = _('Transactions')
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:
            readonly_fields.extend(['manual_deposit_form', 'manual_withdraw_form'])
        return readonly_fields
    
    def manual_deposit_form(self, obj):
        if not obj:
            return _("Save the wallet first to enable manual operations")
        
        deposit_url = reverse('admin:manual_deposit', args=[obj.pk])
        return format_html('''
            <div class="form-row">
                <div style="margin-bottom: 10px;">
                    <label for="id_deposit_amount">{0}:</label>
                    <input type="number" step="0.01" min="0.01" id="id_deposit_amount" name="amount" style="width: 150px;"/>
                </div>
                <div style="margin-bottom: 10px;">
                    <label for="id_deposit_description">{1}:</label>
                    <input type="text" id="id_deposit_description" name="description" style="width: 300px;"/>
                </div>
                <div style="margin-bottom: 10px;">
                    <label for="id_deposit_reference">{2}:</label>
                    <input type="text" id="id_deposit_reference" name="reference" style="width: 200px;"/>
                </div>
                <div>
                    <button type="button" onclick="submitManualOperation('{3}', 'deposit')" 
                    style="background-color: #28a745; color: white; border: none; padding: 5px 15px; cursor: pointer; border-radius: 3px;">
                    {4}</button>
                </div>
            </div>
            <script>
                function submitManualOperation(url, operation) {{
                    var form = document.createElement('form');
                    form.method = 'POST';
                    form.action = url;
                    
                    // Add CSRF token
                    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
                    var csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrfmiddlewaretoken';
                    csrfInput.value = csrfToken;
                    form.appendChild(csrfInput);
                    
                    // Add amount
                    var amountInput = document.createElement('input');
                    amountInput.type = 'hidden';
                    amountInput.name = 'amount';
                    amountInput.value = document.getElementById('id_deposit_amount').value;
                    form.appendChild(amountInput);
                    
                    // Add description
                    var descInput = document.createElement('input');
                    descInput.type = 'hidden';
                    descInput.name = 'description';
                    descInput.value = document.getElementById('id_deposit_description').value;
                    form.appendChild(descInput);
                    
                    // Add reference
                    var refInput = document.createElement('input');
                    refInput.type = 'hidden';
                    refInput.name = 'reference';
                    refInput.value = document.getElementById('id_deposit_reference').value;
                    form.appendChild(refInput);
                    
                    document.body.appendChild(form);
                    form.submit();
                }}
            </script>
        ''', _('Amount'), _('Description'), _('Reference'), deposit_url, _('Deposit Funds'))
    manual_deposit_form.short_description = _('Manual Deposit')
    
    def manual_withdraw_form(self, obj):
        if not obj:
            return _("Save the wallet first to enable manual operations")
        
        withdraw_url = reverse('admin:manual_withdraw', args=[obj.pk])
        return format_html('''
            <div class="form-row">
                <div style="margin-bottom: 10px;">
                    <label for="id_withdraw_amount">{0}:</label>
                    <input type="number" step="0.01" min="0.01" max="{1}" id="id_withdraw_amount" name="amount" style="width: 150px;"/>
                </div>
                <div style="margin-bottom: 10px;">
                    <label for="id_withdraw_description">{2}:</label>
                    <input type="text" id="id_withdraw_description" name="description" style="width: 300px;"/>
                </div>
                <div style="margin-bottom: 10px;">
                    <label for="id_withdraw_reference">{3}:</label>
                    <input type="text" id="id_withdraw_reference" name="reference" style="width: 200px;"/>
                </div>
                <div>
                    <button type="button" onclick="submitManualOperation('{4}', 'withdraw')" 
                    style="background-color: #dc3545; color: white; border: none; padding: 5px 15px; cursor: pointer; border-radius: 3px;">
                    {5}</button>
                </div>
            </div>
        ''', _('Amount'), obj.balance, _('Description'), _('Reference'), withdraw_url, _('Withdraw Funds'))
    manual_withdraw_form.short_description = _('Manual Withdrawal')
    
    @admin.action(description=_('Activate selected wallets'))
    def activate_wallets(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} wallets have been activated.'))
    
    @admin.action(description=_('Deactivate selected wallets'))
    def deactivate_wallets(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} wallets have been deactivated.'))
        
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('wallet/<int:wallet_id>/deposit/', self.admin_site.admin_view(self.manual_deposit_view), name='manual_deposit'),
            path('wallet/<int:wallet_id>/withdraw/', self.admin_site.admin_view(self.manual_withdraw_view), name='manual_withdraw'),
        ]
        return custom_urls + urls
    
    def manual_deposit_view(self, request, wallet_id):
        from django.http import HttpResponseRedirect
        
        wallet = self.get_object(request, wallet_id)
        if wallet is None:
            self.message_user(request, _('Wallet not found'), level=messages.ERROR)
            return HttpResponseRedirect(reverse('admin:user_wallet_changelist'))
        
        if request.method == 'POST':
            form = ManualTransactionForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                description = form.cleaned_data['description'] or _('Admin manual deposit')
                reference = form.cleaned_data['reference'] or f'admin_deposit_{wallet_id}'
                
                try:
                    wallet.deposit(amount, description, reference)
                    self.message_user(
                        request, 
                        _('Successfully deposited {amount} to {user}\'s wallet').format(
                            amount=amount, 
                            user=wallet.user.get_full_name() or wallet.user.phone_number
                        )
                    )
                except Exception as e:
                    self.message_user(request, _('Error: {0}').format(str(e)), level=messages.ERROR)
            else:
                self.message_user(request, _('Invalid form data'), level=messages.ERROR)
        
        return HttpResponseRedirect(reverse('admin:user_wallet_change', args=[wallet_id]))
    
    def manual_withdraw_view(self, request, wallet_id):
        from django.http import HttpResponseRedirect
        
        wallet = self.get_object(request, wallet_id)
        if wallet is None:
            self.message_user(request, _('Wallet not found'), level=messages.ERROR)
            return HttpResponseRedirect(reverse('admin:user_wallet_changelist'))
        
        if request.method == 'POST':
            form = ManualTransactionForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                description = form.cleaned_data['description'] or _('Admin manual withdrawal')
                reference = form.cleaned_data['reference'] or f'admin_withdraw_{wallet_id}'
                
                try:
                    # Check sufficient balance
                    if wallet.balance < amount:
                        raise ValueError(_('Insufficient funds'))
                        
                    wallet.withdraw(amount, description, reference)
                    self.message_user(
                        request, 
                        _('Successfully withdrew {amount} from {user}\'s wallet').format(
                            amount=amount, 
                            user=wallet.user.get_full_name() or wallet.user.phone_number
                        )
                    )
                except Exception as e:
                    self.message_user(request, _('Error: {0}').format(str(e)), level=messages.ERROR)
            else:
                self.message_user(request, _('Invalid form data'), level=messages.ERROR)
        
        return HttpResponseRedirect(reverse('admin:user_wallet_change', args=[wallet_id]))


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ('id', 'wallet_user', 'transaction_type', 'amount_display', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__phone_number', 'description', 'reference')
    readonly_fields = ('wallet', 'amount', 'transaction_type', 'balance_after', 'description', 'reference', 'created_at')
    
    # Unfold customizations
    icon = "swap_horiz"
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Transaction Details'), {
            'fields': ('wallet', 'amount', 'transaction_type', 'description', 'balance_after'),
            'classes': ('tab',),
            # 'tab_icon': 'receipt'
        }),
        (_('Additional Information'), {
            'fields': ('reference', 'created_at'),
            'classes': ('tab',),
            # 'tab_icon': 'more_horiz'
        }),
    )
    
    def wallet_user(self, obj):
        return obj.wallet.user.get_full_name() or obj.wallet.user.phone_number
    wallet_user.short_description = _('User')
    wallet_user.admin_order_field = 'wallet__user__phone_number'
    
    def amount_display(self, obj):
        if obj.amount < 0:
            return format_html('<span style="color: red;">-{}</span>', abs(obj.amount))
        return format_html('<span style="color: green;">+{}</span>', obj.amount)
    amount_display.short_description = _('Amount')
    amount_display.admin_order_field = 'amount'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(TransactionLog)
class TransactionLogAdmin(ModelAdmin):
    list_display = ('id', 'wallet_user', 'action', 'amount_display', 'status',
                    'ip_address', 'created_at')
    list_filter = ('action', 'status', 'created_at')
    search_fields = ('wallet__user__phone_number', 'description', 'reference', 'user__phone_number')
    readonly_fields = ('wallet', 'user', 'action', 'amount', 'balance_before', 'balance_after',
                      'status', 'description', 'reference', 'ip_address', 'created_at')
    
    # Unfold customizations
    icon = "receipt_long"
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Transaction Information'), {
            'fields': ('wallet', 'user', 'action', 'amount', 'status'),
            'classes': ('tab',),
            # 'tab_icon': 'account_balance'
        }),
        (_('Balance Changes'), {
            'fields': ('balance_before', 'balance_after'),
            'classes': ('tab',),
            # 'tab_icon': 'trending_up'
        }),
        (_('Details'), {
            'fields': ('description', 'reference', 'ip_address', 'created_at'),
            'classes': ('tab',),
            # 'tab_icon': 'info'
        }),
    )
    
    def wallet_user(self, obj):
        return obj.wallet.user.get_full_name() or obj.wallet.user.phone_number
    wallet_user.short_description = _('User')
    wallet_user.admin_order_field = 'wallet__user__phone_number'
    
    def amount_display(self, obj):
        if obj.amount < 0:
            return format_html('<span style="color: red;">-{}</span>', abs(obj.amount))
        return format_html('<span style="color: green;">+{}</span>', obj.amount)
    amount_display.short_description = _('Amount')
    amount_display.admin_order_field = 'amount'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ActivityLog)
class ActivityLogAdmin(ModelAdmin):
    list_display = ('id', 'user_display', 'action', 'status', 'ip_address', 'created_at')
    list_filter = ('action', 'status', 'created_at')
    search_fields = ('user__phone_number', 'description', 'user__first_name', 'user__last_name', 'ip_address')
    readonly_fields = ('user', 'action', 'status', 'ip_address', 'user_agent', 
                      'description', 'details_formatted', 'created_at')
    
    # Unfold customizations
    icon = "history"
    list_per_page = 100
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Activity Information'), {
            'fields': ('user', 'action', 'status'),
            'classes': ('tab',),
            # 'tab_icon': 'assignment'
        }),
        (_('Details'), {
            'fields': ('description', 'details_formatted'),
            'classes': ('tab',),
            # 'tab_icon': 'info'
        }),
        (_('Technical Information'), {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('tab',),
            # 'tab_icon': 'computer'
        }),
    )
    
    def user_display(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.phone_number
        return _('Anonymous')
    user_display.short_description = _('User')
    user_display.admin_order_field = 'user__phone_number'
    
    def details_formatted(self, obj):
        if not obj.details:
            return '-'
        
        import json
        from django.utils.safestring import mark_safe
        formatted_json = json.dumps(obj.details, indent=2)
        return mark_safe(f'<pre style="max-height: 300px; overflow-y: auto;">{formatted_json}</pre>')
    details_formatted.short_description = _('Details')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion for cleaning up logs
        return request.user.is_superuser


@admin.register(WalletTransaction)
class WalletTransactionAdmin(ModelAdmin):
    list_display = ('user', 'amount_display', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name', 'description')
    readonly_fields = ('user', 'amount', 'transaction_type', 'reference_code', 'created_at')
    
    # Unfold customizations
    icon = "account_balance_wallet"
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('اطلاعات تراکنش'), {
            'fields': ('user', 'amount', 'transaction_type', 'status'),
            'classes': ('tab',),
            # 'tab_icon': 'info'
        }),
        (_('جزئیات'), {
            'fields': ('description', 'reference_code', 'created_at'),
            'classes': ('tab',),
            # 'tab_icon': 'description'
        }),
    )
    
    def amount_display(self, obj):
        if obj.transaction_type in ['withdraw', 'purchase']:
            return format_html('<span style="color: red;">-{:,} تومان</span>', abs(obj.amount))
        return format_html('<span style="color: green;">+{:,} تومان</span>', obj.amount)
    amount_display.short_description = _('مبلغ')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False



