from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from user.models import User
from blog.models import Article
from course.models import Course
from order.models import Order, Payment

def dashboard_callback(request, context):
    """
    Callback function for the Unfold admin dashboard.
    Provides statistics and recent data for display.
    """
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    week_ago = timezone.now() - timedelta(days=7)
    new_users = User.objects.filter(date_joined__gte=week_ago).count()

    context['user_stats'] = [
        {"label": "کل کاربران", "value": total_users},
        {"label": "کاربران فعال", "value": active_users},
        {"label": "کاربران جدید (7 روز)", "value": new_users},
    ]

    # آمار محتوا
    total_articles = Article.objects.count()
    total_courses = Course.objects.count()
    total_orders = Order.objects.count()
    successful_payments = Payment.objects.filter(status='successful').count()
    total_revenue = Payment.objects.filter(status='successful').aggregate(total=Sum('amount'))['total'] or 0

    context['content_stats'] = [
        {"label": "تعداد مقالات", "value": total_articles},
        {"label": "تعداد دوره‌ها", "value": total_courses},
    ]

    context['order_stats'] = [
        {"label": "کل سفارشات", "value": total_orders},
        {"label": "پرداخت‌های موفق", "value": successful_payments},
        {"label": "درآمد کل (تومان)", "value": f"{total_revenue:,}"},
    ]

    # نمودار فعالیت
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # آمار کاربران جدید
    daily_users = (
        User.objects.filter(date_joined__gte=thirty_days_ago)
        .extra({"date": "date(date_joined)"})
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    # آمار سفارشات
    daily_orders = (
        Order.objects.filter(created_at__gte=thirty_days_ago)
        .extra({"date": "date(created_at)"})
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    # تبدیل به دیکشنری برای دسترسی آسان‌تر
    orders_dict = {str(item["date"]): item["count"] for item in daily_orders}
    
    # ترکیب داده‌ها برای نمودار
    dates = [str(item["date"]) for item in daily_users]
    users_data = [item["count"] for item in daily_users]
    orders_data = [orders_dict.get(date, 0) for date in dates]

    context['chart_data'] = {
        "labels": dates,
        "datasets": [
            {
                "label": "کاربران جدید",
                "data": users_data,
                "borderColor": "#6366f1",
                "backgroundColor": "rgba(99, 102, 241, 0.2)",
                "tension": 0.4
            },
            {
                "label": "سفارشات",
                "data": orders_data,
                "borderColor": "#10b981",
                "backgroundColor": "rgba(16, 185, 129, 0.2)",
                "tension": 0.4
            }
        ]
    }

    return context 