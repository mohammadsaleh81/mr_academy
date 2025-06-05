from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, FloatField
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)

    class Meta:
        abstract = True

class Course(AbstractBaseModel):
    LEVEL_CHOICES = [
        ('beginner', _('مبتدی')),
        ('intermediate', _('متوسط')),
        ('advanced', _('پیشرفته')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('پیش‌نویس')),
        ('published', _('منتشر شده')),
        ('archived', _('آرشیو شده')),
    ]

    title = models.CharField(_('عنوان'), max_length=200)
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True)
    description = models.TextField(_('توضیحات'))
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                 related_name='courses', verbose_name=_('مدرس'))
    thumbnail = models.ImageField(_('تصویر شاخص'), upload_to='courses/thumbnails/', null=True, blank=True)
    price = models.DecimalField(_('قیمت'), max_digits=10, decimal_places=2, default=0)
    is_free = models.BooleanField(_('رایگان'), default=False)
    status = models.CharField(_('وضعیت'), max_length=20, choices=STATUS_CHOICES, default='draft')
    level = models.CharField(_('سطح'), max_length=20, choices=LEVEL_CHOICES, default='beginner')
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, 
                                         related_name='required_for', verbose_name=_('پیش‌نیازها'))
    tags = models.ManyToManyField('Tag', blank=True, related_name='courses', verbose_name=_('برچسب‌ها'))
    estimated_duration = models.PositiveIntegerField(_('مدت زمان تقریبی (ساعت)'), null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('دوره')
        verbose_name_plural = _('دوره‌ها')
        indexes = [
            models.Index(fields=['status', 'level']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_free:
            self.price = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_student_count(self):
        return self.enrollments.count()

    def get_total_duration(self):
        return sum(chapter.get_duration() for chapter in self.chapters.all())

    def get_total_chapters(self):
        return self.chapters.all().count()

    def get_total_lessons(self):
        return sum(chapter.get_total_lessons() for chapter in self.chapters.all())


    def get_average_rating(self):
        return self.ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    def get_completion_rate(self):
        total_students = self.get_student_count()
        if total_students == 0:
            return 0
        completed_students = self.enrollments.filter(progress__is_completed=True).count()
        return (completed_students / total_students) * 100

    @property
    def is_published(self):
        return self.status == 'published'

class Tag(models.Model):
    name = models.CharField(_('نام'), max_length=50, unique=True)
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Chapter(AbstractBaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name=_('دوره'))
    title = models.CharField(_('عنوان'), max_length=200)
    description = models.TextField(_('توضیحات'), blank=True)
    order = models.PositiveIntegerField(_('ترتیب'))

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
        verbose_name = _('فصل')
        verbose_name_plural = _('فصل‌ها')

    def __str__(self):
        return f"{self.course.title} - فصل {self.order}: {self.title}"

    def get_duration(self):
        return sum(lesson.duration or 0 for lesson in self.lessons.all())


    def get_total_lessons(self):
        return self.lessons.all().count()


class Lesson(AbstractBaseModel):
    CONTENT_TYPE_CHOICES = [
        ('video', _('ویدیو')),
        ('text', _('متن')),
        ('quiz', _('آزمون')),
        ('assignment', _('تکلیف')),
    ]

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons', verbose_name=_('فصل'))
    title = models.CharField(_('عنوان'), max_length=200)
    content = models.TextField(_('محتوا'))
    content_type = models.CharField(_('نوع محتوا'), max_length=20, choices=CONTENT_TYPE_CHOICES, default='video')
    video_url = models.URLField(_('آدرس ویدیو'), blank=True, null=True)
    duration = models.PositiveIntegerField(_('مدت زمان'), help_text=_("مدت زمان به دقیقه"), null=True, blank=True)
    order = models.PositiveIntegerField(_('ترتیب'))
    is_free_preview = models.BooleanField(_('پیش‌نمایش رایگان'), default=False)
    points = models.PositiveIntegerField(_('امتیاز'), default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['chapter', 'order']
        verbose_name = _('درس')
        verbose_name_plural = _('درس‌ها')

    def __str__(self):
        return f"{self.chapter.course.title} - {self.chapter.title} - درس {self.order}: {self.title}"

    def clean(self):
        if self.content_type == 'video' and not self.video_url:
            raise ValidationError(_('برای محتوای ویدیویی، آدرس ویدیو الزامی است.'))

class CourseRating(AbstractBaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings', verbose_name=_('دوره'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='course_ratings', verbose_name=_('کاربر'))
    rating = models.PositiveSmallIntegerField(_('امتیاز'), 
                                            validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(_('نظر'), blank=True)

    class Meta:
        unique_together = ['course', 'user']
        verbose_name = _('امتیاز دوره')
        verbose_name_plural = _('امتیازهای دوره')
        indexes = [
            models.Index(fields=['course', 'rating']),
        ]

    def __str__(self):
        return f"{self.user.email} rated {self.course.title}: {self.rating}"

class LessonProgress(models.Model):
    COMPLETION_STATUS = (
        ('not_started', _('شروع نشده')),
        ('in_progress', _('در حال یادگیری')),
        ('completed', _('تکمیل شده')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress', verbose_name=_('کاربر'))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress', verbose_name=_('درس'))
    status = models.CharField(_('وضعیت'), max_length=20, choices=COMPLETION_STATUS, default='not_started')
    is_completed = models.BooleanField(_('تکمیل شده'), default=False)
    watched_duration = models.PositiveIntegerField(_('مدت زمان مشاهده شده'), default=0)
    last_position = models.PositiveIntegerField(_('آخرین موقعیت'), default=0)
    completion_date = models.DateTimeField(_('تاریخ تکمیل'), null=True, blank=True)
    last_activity = models.DateTimeField(_('آخرین فعالیت'), auto_now=True)
    notes = models.TextField(_('یادداشت‌های کاربر'), blank=True)
    rating = models.PositiveSmallIntegerField(
        _('امتیاز درس'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['lesson__chapter__order', 'lesson__order']
        verbose_name = _('پیشرفت درس')
        verbose_name_plural = _('پیشرفت‌های درس')
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['user', 'lesson', 'status']),
            models.Index(fields=['completion_date']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Update status based on progress
        if self.is_completed and self.status != 'completed':
            self.status = 'completed'
            self.completion_date = timezone.now()
        elif self.watched_duration > 0 and self.status == 'not_started':
            self.status = 'in_progress'
        
        super().save(*args, **kwargs)
        
        # Update course progress
        self.update_course_progress()

    def mark_completed(self):
        if not self.is_completed:
            self.is_completed = True
            self.completion_date = timezone.now()
            self.status = 'completed'
            self.save()

    def update_progress(self, position, duration=None):
        """Update progress based on video position or other metrics."""
        self.last_position = position
        if duration:
            self.watched_duration = duration
        
        # Mark as completed if watched more than 90% of the video
        if self.lesson.duration and self.watched_duration >= (self.lesson.duration * 0.9):
            self.mark_completed()
        elif self.status == 'not_started':
            self.status = 'in_progress'
            self.save()

    def update_course_progress(self):
        """Update the course progress when a lesson is completed."""
        enrollment = Enrollment.objects.get(
            user=self.user,
            course=self.lesson.chapter.course
        )
        enrollment.update_progress()

class CourseProgress:
    """Helper class for calculating course progress metrics."""
    
    def __init__(self, user, course):
        self.user = user
        self.course = course
        self.enrollment = course.enrollments.get(user=user)

    @property
    def total_lessons(self):
        return self.course.chapters.aggregate(
            total=Count('lessons')
        )['total']

    @property
    def completed_lessons(self):
        return LessonProgress.objects.filter(
            user=self.user,
            lesson__chapter__course=self.course,
            is_completed=True
        ).count()

    @property
    def in_progress_lessons(self):
        return LessonProgress.objects.filter(
            user=self.user,
            lesson__chapter__course=self.course,
            status='in_progress'
        ).count()

    @property
    def completion_percentage(self):
        if not self.total_lessons:
            return 0
        return (self.completed_lessons / self.total_lessons) * 100

    @property
    def total_duration(self):
        return self.course.chapters.aggregate(
            total=Sum('lessons__duration')
        )['total'] or 0

    @property
    def watched_duration(self):
        return LessonProgress.objects.filter(
            user=self.user,
            lesson__chapter__course=self.course
        ).aggregate(
            total=Sum('watched_duration')
        )['total'] or 0

    @property
    def time_spent_percentage(self):
        if not self.total_duration:
            return 0
        return (self.watched_duration / self.total_duration) * 100

    @property
    def last_activity(self):
        last_progress = LessonProgress.objects.filter(
            user=self.user,
            lesson__chapter__course=self.course
        ).order_by('-last_activity').first()
        
        return last_progress.last_activity if last_progress else None

    def get_chapter_progress(self, chapter):
        """Get progress details for a specific chapter."""
        chapter_lessons = chapter.lessons.count()
        if not chapter_lessons:
            return 0
            
        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            lesson__chapter=chapter,
            is_completed=True
        ).count()
        
        return (completed_lessons / chapter_lessons) * 100

    def get_next_lesson(self):
        """Get the next uncompleted lesson."""
        return Lesson.objects.filter(
            chapter__course=self.course
        ).exclude(
            progress__user=self.user,
            progress__is_completed=True
        ).order_by(
            'chapter__order',
            'order'
        ).first()

class Discount(AbstractBaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discounts', verbose_name=_('دوره'))
    code = models.CharField(_('کد تخفیف'), max_length=50, unique=True)
    percentage = models.PositiveIntegerField(
        _('درصد تخفیف'),
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    start_date = models.DateTimeField(_('تاریخ شروع'))
    end_date = models.DateTimeField(_('تاریخ پایان'))
    is_active = models.BooleanField(_('فعال'), default=True)
    max_uses = models.PositiveIntegerField(_('حداکثر استفاده'), null=True, blank=True)
    current_uses = models.PositiveIntegerField(_('تعداد استفاده فعلی'), default=0)
    min_course_price = models.DecimalField(_('حداقل قیمت دوره'), max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = _('تخفیف')
        verbose_name_plural = _('تخفیف‌ها')
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.code} - {self.percentage}% تخفیف برای {self.course.title}"

    def is_valid(self, course=None):
        now = timezone.now()
        
        if not self.is_active:
            return False, _('کد تخفیف غیرفعال است.')
            
        if self.start_date > now:
            return False, _('کد تخفیف هنوز فعال نشده است.')
            
        if self.end_date < now:
            return False, _('کد تخفیف منقضی شده است.')
            
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, _('کد تخفیف به حداکثر استفاده رسیده است.')
            
        if course and self.min_course_price and course.price < self.min_course_price:
            return False, _('قیمت دوره کمتر از حداقل قیمت مجاز برای استفاده از کد تخفیف است.')
            
        return True, _('کد تخفیف معتبر است.')

    @transaction.atomic
    def apply_discount(self, course):
        is_valid, message = self.is_valid(course)
        if not is_valid:
            raise ValidationError(message)
            
        self.current_uses += 1
        self.save()
        
        discounted_price = course.price * (100 - self.percentage) / 100
        return discounted_price

class Enrollment(AbstractBaseModel):
    STATUS_CHOICES = [
        ('active', _('فعال')),
        ('completed', _('تکمیل شده')),
        ('expired', _('منقضی شده')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='enrollments', verbose_name=_('کاربر'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, 
                              related_name='enrollments', verbose_name=_('دوره'))
    price_paid = models.DecimalField(_('مبلغ پرداخت شده'), max_digits=10, decimal_places=2)
    discount_used = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name=_('تخفیف استفاده شده'))
    status = models.CharField(_('وضعیت'), max_length=20, choices=STATUS_CHOICES, default='active')
    completion_date = models.DateTimeField(_('تاریخ تکمیل'), null=True, blank=True)

    class Meta:
        unique_together = ['user', 'course']
        verbose_name = _('ثبت‌نام')
        verbose_name_plural = _('ثبت‌نام‌ها')
        indexes = [
            models.Index(fields=['user', 'course', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"

    def mark_completed(self):
        if self.status != 'completed':
            self.status = 'completed'
            self.completion_date = timezone.now()
            self.save()

    def get_progress_percentage(self):
        total_lessons = self.course.chapters.aggregate(
            total=Count('lessons')
        )['total']
        
        if not total_lessons:
            return 0
            
        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            lesson__chapter__course=self.course,
            is_completed=True
        ).count()
        
        return (completed_lessons / total_lessons) * 100

    def update_progress(self):
        """Update progress metrics for this enrollment."""
        progress = CourseProgress(self.user, self.course)
        
        if progress.completion_percentage == 100:
            self.status = 'completed'
            self.completion_date = timezone.now()
            self.save()

    @property
    def progress_metrics(self):
        """Get detailed progress metrics for this enrollment."""
        progress = CourseProgress(self.user, self.course)
        return {
            'completion_percentage': progress.completion_percentage,
            'completed_lessons': progress.completed_lessons,
            'total_lessons': progress.total_lessons,
            'in_progress_lessons': progress.in_progress_lessons,
            'watched_duration': progress.watched_duration,
            'total_duration': progress.total_duration,
            'time_spent_percentage': progress.time_spent_percentage,
            'last_activity': progress.last_activity
        }



class Comment(AbstractBaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments', verbose_name=_('دوره'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_comments', verbose_name=_('کاربر'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name=_('کامنت والد'))
    content = models.TextField(_('محتوا'))
    is_approved = models.BooleanField(_('تایید شده'), default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')
        indexes = [
            models.Index(fields=['course', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"نظر {self.user.email} برای {self.course.title}"

    @property
    def is_reply(self):
        return self.parent is not None

    def get_replies(self):
        return Comment.objects.filter(parent=self)
