import django_filters
from django.utils.translation import gettext_lazy as _
from .models import Order, Payment

class OrderFilter(django_filters.FilterSet):
    min_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    paid_after = django_filters.DateTimeFilter(field_name='paid_at', lookup_expr='gte')
    paid_before = django_filters.DateTimeFilter(field_name='paid_at', lookup_expr='lte')
    
    has_items = django_filters.BooleanFilter(field_name='items', method='filter_has_items')
    
    class Meta:
        model = Order
        fields = {
            'order_number': ['exact', 'contains'],
            'status': ['exact'],
        }
        
    def filter_has_items(self, queryset, name, value):
        if value:
            return queryset.filter(items__isnull=False).distinct()
        return queryset.filter(items__isnull=True)

class PaymentFilter(django_filters.FilterSet):
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    payment_method = django_filters.ChoiceFilter(choices=Payment.PAYMENT_METHODS)
    status = django_filters.ChoiceFilter(choices=Payment.STATUS_CHOICES)
    
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Payment
        fields = {
            'transaction_id': ['exact'],
            'payment_method': ['exact'],
            'status': ['exact'],
        } 