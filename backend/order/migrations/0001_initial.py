# Generated by Django 4.2 on 2025-05-25 22:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=32, unique=True, verbose_name='شماره سفارش')),
                ('status', models.CharField(choices=[('pending', 'در انتظار پرداخت'), ('processing', 'در حال پردازش'), ('completed', 'تکمیل شده'), ('cancelled', 'لغو شده'), ('refunded', 'مسترد شده')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='مبلغ کل')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='تاریخ پرداخت')),
                ('notes', models.TextField(blank=True, verbose_name='یادداشت\u200cها')),
            ],
            options={
                'verbose_name': 'سفارش',
                'verbose_name_plural': 'سفارش\u200cها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='مبلغ')),
                ('payment_method', models.CharField(choices=[('online', 'پرداخت آنلاین'), ('wallet', 'کیف پول'), ('bank_transfer', 'انتقال بانکی')], max_length=20, verbose_name='روش پرداخت')),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='شناسه تراکنش')),
                ('status', models.CharField(choices=[('pending', 'در انتظار پرداخت'), ('successful', 'موفق'), ('failed', 'ناموفق'), ('refunded', 'مسترد شده')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('wallet_transaction', models.CharField(blank=True, max_length=100, null=True, verbose_name='تراکنش کیف پول')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('refund_transaction_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='شناسه تراکنش استرداد')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='order.order', verbose_name='سفارش')),
            ],
            options={
                'verbose_name': 'پرداخت',
                'verbose_name_plural': 'پرداخت\u200cها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(verbose_name='شناسه محتوا')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='تعداد')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='قیمت')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='نوع محتوا')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='order.order', verbose_name='سفارش')),
            ],
            options={
                'verbose_name': 'آیتم سفارش',
                'verbose_name_plural': 'آیتم\u200cهای سفارش',
                'ordering': ['id'],
            },
        ),
    ]
