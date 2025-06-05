from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Course, Chapter, Lesson, Discount, Enrollment, Comment


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    fields = ['user', 'content', 'created_at', 'is_approved']
    readonly_fields = ['user', 'content', 'created_at', ]
    classes = ['tab-comment']
    verbose_name = _('Comment')
    verbose_name_plural = _('Comment')
    can_delete = True
    tab = True


class LessonInline(StackedInline):
    model = Lesson
    extra = 1
    fields = ['title', 'content', 'video_url', 'duration', 'is_free_preview']
    classes = ['tab-lesson']
    verbose_name = 'Lesson'
    verbose_name_plural = 'Lessons'
    tab = True

class ChapterInline(TabularInline):
    model = Chapter
    extra = 1
    fields = ['title', 'description', ]
    classes = ['tab-chapter']
    verbose_name = 'Chapter'
    verbose_name_plural = 'Chapters'
    show_change_link = True
    tab = True

@admin.register(Chapter)
class ChapterAdmin(ModelAdmin):
    list_display = ['title', 'course', 'lessons_count']
    list_filter = ['course']
    search_fields = ['title', 'description', 'course__title']
    inlines = [LessonInline]
    ordering = ['course', 'order']

    def lessons_count(self, obj):
        count = obj.lessons.count()
        return format_html('<span style="color: #666;">{} {}</span>', count, _('درس'))
    lessons_count.short_description = _('تعداد درس‌ها')

class EnrollmentInline(TabularInline):
    model = Enrollment
    extra = 0
    fields = ['user', 'created_at', 'price_paid', 'discount_used']
    classes = ['tab-enrollment']
    verbose_name = _('Enrollment')
    verbose_name_plural = _('Enrollment')
    readonly_fields = ['created_at', 'user', 'price_paid', 'discount_used']
    can_delete = False
    tab = True

class DiscountInline(TabularInline):
    model = Discount
    extra = 0
    fields = ['code', 'percentage', 'start_date', 'end_date', 'is_active', 'max_uses', 'current_uses']
    classes = ['tab-discount']
    verbose_name = _('Discount')
    verbose_name_plural = _('Discount')
    show_change_link = True
    tab = True

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ['title_with_thumbnail', 'instructor', 'price_display', 'is_free', 'status', 'created_at', 'students_count']
    list_filter = ['is_free', 'status', 'created_at', 'level']
    search_fields = ['title', 'description', 'instructor__email']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ChapterInline, EnrollmentInline, DiscountInline, CommentInline]
    actions = ['make_published', 'make_draft']
    
    fieldsets = [
        (_("اطلاعات پایه"), {
            "fields": (
                ('title', 'slug'),
                ('instructor', 'estimated_duration', 'level'),
                'prerequisites',
                'tags',

                'description',


            ),
            'classes': ('tab',)

        }),
        (_("قیمت‌گذاری و وضعیت"), {
            "fields": (
                ('price', 'is_free'),
                'status',
            ),
            'classes': ('tab',)

        }),
        # (_("جزئیات دوره"), {
        #     "fields": (
        #         'level',
        #         # 'duration',
        #         # 'prerequisites',
        #         # 'what_you_will_learn',
        #     ),
        #     'classes': ('tab',)

        # }),

    ]

    def title_with_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" style="width: 50px; height: 50px; margin-right: 10px; border-radius: 5px; object-fit: cover;">'
                '<span>{}</span>'
                '</div>',
                obj.thumbnail.url, obj.title
            )
        return obj.title
    title_with_thumbnail.short_description = _('دوره')

    def price_display(self, obj):
        if obj.is_free:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', _('رایگان'))
        formatted_price = "{:,.0f}".format(float(obj.price))
        return format_html('<span style="color: #e44d26; font-weight: bold;">{} تومان</span>', formatted_price)
    price_display.short_description = _('قیمت')

    def students_count(self, obj):
        count = obj.enrollments.count()
        return format_html('<span style="background-color: #f0f0f0; padding: 4px 8px; border-radius: 12px;">{}</span>', count)
    students_count.short_description = _('تعداد دانشجویان')

    @admin.action(description=_('انتشار دوره‌های انتخاب شده'))
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} دوره با موفقیت منتشر شد.')

    @admin.action(description=_('تبدیل به پیش‌نویس دوره‌های انتخاب شده'))
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} دوره به پیش‌نویس تبدیل شد.')

@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ['title', 'chapter_course', 'chapter', 'order', 'duration_display', 'preview_status']
    list_filter = ['chapter__course', 'is_free_preview', 'content_type']
    search_fields = ['title', 'content']
    ordering = ['chapter__course', 'chapter', 'order']

    def chapter_course(self, obj):
        return obj.chapter.course
    chapter_course.short_description = _('دوره')

    def duration_display(self, obj):
        if obj.duration:
            return format_html('{} {}', obj.duration, _('دقیقه'))
        return '-'
    duration_display.short_description = _('مدت زمان')

    def preview_status(self, obj):
        if obj.is_free_preview:
            return format_html('<span style="color: green;">✓ {}</span>', _('پیش‌نمایش رایگان'))
        return format_html('<span style="color: #666;">-</span>')
    preview_status.short_description = _('پیش‌نمایش')

@admin.register(Discount)
class DiscountAdmin(ModelAdmin):
    list_display = ['code', 'course', 'discount_display', 'status_display', 'usage_display', 'validity_period']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['code', 'course__title']
    
    fieldsets = (
        (_('اطلاعات تخفیف'), {
            'fields': ('code', 'course', 'percentage'),
            'classes': ('collapse')

        }),
        (_('اعتبار'), {
            'fields': ('start_date', 'end_date', 'is_active'),
            'classes': ('collapse',)
        }),
        (_('محدودیت استفاده'), {
            'fields': ('max_uses', 'current_uses', 'min_course_price'),
            'classes': ('collapse',)
        }),
    )

    def discount_display(self, obj):
        return format_html('<span style="color: #e44d26;">{}</span>%', obj.percentage)
    discount_display.short_description = _('تخفیف')

    def status_display(self, obj):
        is_valid, message = obj.is_valid()
        if is_valid:
            return format_html('<span style="color: green;">{}</span>', _('فعال'))
        return format_html(
            '<span style="color: red;" title="{}">{}</span>', 
            message, _('غیرفعال')
        )
    status_display.short_description = _('وضعیت')

    def usage_display(self, obj):
        if obj.max_uses:
            return format_html('{}/{} {}', obj.current_uses, obj.max_uses, _('استفاده'))
        return format_html('{} {}', obj.current_uses, _('استفاده'))
    usage_display.short_description = _('استفاده')

    def validity_period(self, obj):
        return format_html('{} {} {}', obj.start_date.strftime('%Y-%m-%d'), _('تا'), obj.end_date.strftime('%Y-%m-%d'))
    validity_period.short_description = _('دوره اعتبار')

@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ['user', 'course', 'created_at', 'payment_display', 'discount_info']
    list_filter = ['created_at', 'course', 'status']
    search_fields = ['user__email', 'course__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    def payment_display(self, obj):
        return format_html('{} {}', obj.price_paid, _('تومان'))
    payment_display.short_description = _('مبلغ پرداخت شده')

    def discount_info(self, obj):
        if obj.discount_used:
            return format_html(
                '<span style="color: #e44d26;">{} ({}%)</span>',
                obj.discount_used.code,
                obj.discount_used.percentage
            )
        return '-'
    discount_info.short_description = _('تخفیف')