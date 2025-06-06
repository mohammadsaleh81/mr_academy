from django.contrib import admin
from payment.models import  Payment
# Register your models here.
from unfold.admin import ModelAdmin, TabularInline, StackedInline

@admin.register(Payment)
class PayAdmin(ModelAdmin):
    list_display = ['user', 'status', 'pay_local_id', 'authority']
    readonly_fields = ['created_at', 'updated_at', 'user',  'pay_local_id', 'authority', 'amount']