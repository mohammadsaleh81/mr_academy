from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['content_type', 'object_id', 'quantity', 'price', 'total_price']
    
    def total_price(self, obj):
        return obj.total_price if obj else '-'
    total_price.short_description = _('Total Price')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['payment_method', 'amount', 'transaction_id', 'status', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user_info', 'total_amount', 'status', 'created_at', 'payment_status']
    list_filter = ['status', 'created_at', 'paid_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at']
    inlines = [OrderItemInline, PaymentInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )

    def user_info(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{} ({})</a>', url, obj.user.username, obj.user.email)
        return '-'
    user_info.short_description = _('User')
    
    def payment_status(self, obj):
        payment = obj.payments.last()
        if payment:
            status_colors = {
                'pending': 'orange',
                'successful': 'green',
                'failed': 'red'
            }
            color = status_colors.get(payment.status, 'black')
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                payment.get_status_display()
            )
        return '-'
    payment_status.short_description = _('Payment Status')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_link', 'content_type', 'object_id', 'quantity', 'price', 'total_price']
    list_filter = ['content_type', 'order__status']
    search_fields = ['order__order_number', 'order__user__username']
    readonly_fields = ['total_price']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:order_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = _('Order')
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = _('Total Price')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order_link', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'order__user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('order', 'amount', 'payment_method', 'transaction_id', 'status')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:order_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '-'
    order_link.short_description = _('Order')
