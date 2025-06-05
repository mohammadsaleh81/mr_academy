from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def admin_page(app, model):
    try:
        return reverse_lazy(f"admin:{app}_{model}_changelist")
    except (LookupError, TypeError) as e:
        raise ValueError(f"اپلیکیشن '{app}' یا مدل '{model}' پیدا نشد. خطا: {str(e)}")


def create_sidebar_item(app, model, title, icon):
    return {
        "title": _(title),
        "icon": icon,
        "link": admin_page(app, model),
    }


# نگاشت آیکون‌ها برای یکپارچگی و سهولت استفاده
ICON_MAP = {
    # کاربران و احراز هویت
    'group': 'groups',
    'user': 'person',
    
    # وبلاگ
    'article': 'interpreter_mode',
    'category': 'nest_gale_wifi',
    'tag': 'tag',
    'comment': 'interpreter_mode',
    'rating': 'brand_family',
    
    # رسانه
    'media': 'media_output',
    'podcast': 'media_output',
    'video': 'videocam',
    'file': 'dns',
    'livestream': 'videocam',
    
    # دوره‌ها
    'course': 'school',
    'chapter': 'menu_book',
    'lesson': 'class',
    'discount': 'local_offer',
    'enrollment': 'how_to_reg',
    
    # سفارشات
    'order': 'shopping_cart',
    'payment': 'payments',
    
    # عمومی
    'dashboard': 'domain',
    'settings': 'dns',
}


# تعریف آیتم‌های نوار کناری به صورت پویا
user_list = [
    create_sidebar_item('auth', 'group', 'گروه‌ها', ICON_MAP['group']),
    create_sidebar_item('user', 'user', 'کاربران', ICON_MAP['user']),
]

blog_list = [
    create_sidebar_item('blog', 'article', 'مقالات', ICON_MAP['article']),
    create_sidebar_item('blog', 'category', 'دسته‌بندی‌ها', ICON_MAP['category']),
    create_sidebar_item('blog', 'tag', 'برچسب‌ها', ICON_MAP['tag']),
    create_sidebar_item('blog', 'comment', 'نظرات', ICON_MAP['comment']),
    create_sidebar_item('blog', 'rating', 'امتیازها', ICON_MAP['rating']),
]

media_list = [
    create_sidebar_item('blog', 'mediacategory', 'دسته‌بندی‌ها', ICON_MAP['category']),
    create_sidebar_item('blog', 'podcast', 'پادکست‌ها', ICON_MAP['podcast']),
    create_sidebar_item('blog', 'video', 'ویدیوها', ICON_MAP['video']),
    create_sidebar_item('blog', 'file', 'فایل‌ها', ICON_MAP['file']),
    create_sidebar_item('blog', 'livestream', 'پخش زنده', ICON_MAP['livestream']),
    create_sidebar_item('blog', 'mediacomment', 'نظرات', ICON_MAP['comment']),
]

course_list = [
    create_sidebar_item('course', 'course', 'دوره‌ها', ICON_MAP['course']),
    # create_sidebar_item('course', 'chapter', 'فصل‌ها', ICON_MAP['chapter']),
    # create_sidebar_item('course', 'lesson', 'درس‌ها', ICON_MAP['lesson']),
    create_sidebar_item('course', 'discount', 'تخفیف‌ها', ICON_MAP['discount']),
    create_sidebar_item('course', 'enrollment', 'ثبت‌نام‌ها', ICON_MAP['enrollment']),
]

order_list = [
    create_sidebar_item('order', 'order', 'سفارش‌ها', ICON_MAP['order']),
    create_sidebar_item('order', 'payment', 'پرداخت‌ها', ICON_MAP['payment']),
]

def create_sidebar_section(title, icon, items):
    return {
        "title": _(title),
        "collapsible": True,
        "icon": icon,
        "items": items,
    }


# ساختار نوار کناری
SIDEBAR = [
    create_sidebar_section(_("کاربران و گروه‌ها"), ICON_MAP['user'], user_list),
    create_sidebar_section(_("دوره‌های آموزشی"), ICON_MAP['course'], course_list),
    create_sidebar_section(_("مدیریت محتوا"), ICON_MAP['article'], blog_list),
    create_sidebar_section(_("رسانه‌ها"), ICON_MAP['media'], media_list),
    create_sidebar_section(_("سفارشات"), ICON_MAP['order'], order_list),
]


# تابع بررسی دسترسی
def permission_callback(request):
    return request.user.is_superuser


# تابع نمایش نشان
def badge_callback(request):
    from blog.models import Comment
    return Comment.objects.filter(is_approved=False).count()