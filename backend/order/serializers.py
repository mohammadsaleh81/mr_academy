from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .models import Order, OrderItem, Payment

class OrderItemSerializer(serializers.ModelSerializer):
    content_type_str = serializers.CharField(write_only=True, required=False)
    item_title = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'item_type', 'course_id', 'content_type_str', 
            'object_id', 'quantity', 'price', 'total_price', 
            'item_title'
        ]
        read_only_fields = ['price']

    def get_item_title(self, obj):
        try:
            item = obj.get_item()
            return str(item)
        except:
            return "Unknown Item"

    def validate(self, data):
        item_type = data.get('item_type', 'course')
        
        if item_type == 'course':
            course_id = data.get('course_id')
            if not course_id:
                raise serializers.ValidationError(_("برای آیتم‌های دوره، شناسه دوره الزامی است."))
                
            try:
                from course.models import Course
                course = Course.objects.get(id=course_id)
                data['course'] = course
                data['price'] = course.price
            except Course.DoesNotExist:
                raise serializers.ValidationError(_("دوره مورد نظر یافت نشد."))
                
            # Remove helper fields
            data.pop('course_id', None)
            data.pop('content_type_str', None)
            data.pop('object_id', None)
            
        else:
            if not data.get('content_type_str') or not data.get('object_id'):
                raise serializers.ValidationError(_("برای آیتم‌های غیر دوره، نوع محتوا و شناسه محتوا الزامی است."))
                
            try:
                app_label, model = data['content_type_str'].split('.')
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                item = content_type.get_object_for_this_type(id=data['object_id'])
                
                # Get the price from the item
                if hasattr(item, 'price'):
                    data['price'] = item.price
                else:
                    raise serializers.ValidationError(_("آیتم انتخاب شده قیمت ندارد."))
                    
                # Remove helper field and set content_type
                data.pop('content_type_str')
                data['content_type'] = content_type
                data.pop('course_id', None)
                
            except (ContentType.DoesNotExist, ValueError):
                raise serializers.ValidationError(_("نوع محتوا نامعتبر است. از فرمت 'app_label.model' استفاده کنید."))
            except Exception as e:
                raise serializers.ValidationError(str(e))
            
        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_method',
            'transaction_id', 'status', 'wallet_transaction',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['transaction_id', 'status', 'wallet_transaction']

    def validate(self, data):
        if data['amount'] <= 0:
            raise serializers.ValidationError(_("Amount must be greater than zero"))
            
        if data['amount'] > data['order'].total_amount:
            raise serializers.ValidationError(_("Payment amount cannot exceed order total"))
            
        return data

class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total_amount', 'created_at', 'paid_at'
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'total_amount', 'created_at', 'updated_at', 'paid_at',
            'items', 'payments'
        ]
        read_only_fields = [
            'order_number', 'user', 'status', 'total_amount',
            'paid_at'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate total amount
        total_amount = sum(
            item['quantity'] * item['price']
            for item in items_data
        )
        
        # Create order
        order = Order.objects.create(
            user=self.context['request'].user,
            total_amount=total_amount,
            order_number=Order.generate_order_number()  # You need to implement this method
        )
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['order', 'amount', 'payment_method']

    def validate(self, data):
        order = data['order']
        
        # Check if order belongs to the current user
        if order.user != self.context['request'].user:
            raise serializers.ValidationError(_("You cannot make payment for this order"))
            
        # Check if order is in pending status
        if order.status != 'pending':
            raise serializers.ValidationError(_("This order is not in pending status"))
            
        # Validate payment amount
        remaining_amount = order.total_amount - order.payments.filter(
            status='successful'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        if data['amount'] > remaining_amount:
            raise serializers.ValidationError(
                _("Payment amount ({amount}) exceeds remaining order amount ({remaining})").format(
                    amount=data['amount'],
                    remaining=remaining_amount
                )
            )
            
        return data

    def create(self, validated_data):
        payment = super().create(validated_data)
        
        # If payment method is wallet, process it immediately
        if validated_data['payment_method'] == 'wallet':
            payment.process_wallet_payment()
        
        return payment 