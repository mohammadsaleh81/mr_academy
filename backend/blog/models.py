from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


class Category(models.Model):
    name = models.CharField(_('نام'), max_length=100)
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True)
    description = models.TextField(_('توضیحات'), blank=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('دسته‌بندی')
        verbose_name_plural = _('دسته‌بندی‌ها')
        ordering = ['name']


class Tag(models.Model):
    name = models.CharField(_('نام'), max_length=50)
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('برچسب')
        verbose_name_plural = _('برچسب‌ها')
        ordering = ['name']


class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', _('پیش‌نویس')),
        ('published', _('منتشر شده')),
    )
    
    title = models.CharField(_('عنوان'), max_length=200)
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True)
    content = models.TextField(_('محتوا'))
    summary = models.TextField(_('خلاصه'), blank=True)
    featured_image = models.ImageField(_('تصویر شاخص'), upload_to='blog/articles/', blank=True)
    thumbnail = models.ImageField(_('کاور'), upload_to='blog/thumbnails/', blank=True)
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('نویسنده')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name=_('دسته‌بندی')
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='articles',
        blank=True,
        verbose_name=_('برچسب‌ها')
    )
    
    status = models.CharField(_('وضعیت'), max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)
    published_at = models.DateTimeField(_('تاریخ انتشار'), null=True, blank=True)
    
    # User interactions
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ArticleLike',
        related_name='liked_articles',
        verbose_name=_('پسندها')
    )
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ArticleBookmark',
        related_name='bookmarked_articles',
        verbose_name=_('نشان‌شده‌ها')
    )
    view_count = models.PositiveIntegerField(_('تعداد بازدید'), default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('مقاله')
        verbose_name_plural = _('مقالات')
        ordering = ['-created_at']


class ArticleLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=_('مقاله'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        verbose_name = _('پسند مقاله')
        verbose_name_plural = _('پسندهای مقاله')

    def __str__(self):
        return f'پسند {self.user} برای {self.article}'


class ArticleBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=_('مقاله'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        verbose_name = _('نشان‌شده مقاله')
        verbose_name_plural = _('نشان‌شده‌های مقاله')

    def __str__(self):
        return f'نشان‌شده {self.user} برای {self.article}'


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('مقاله')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        verbose_name=_('نویسنده')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('نظر والد')
    )
    content = models.TextField(_('محتوا'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)
    is_approved = models.BooleanField(_('تایید شده'), default=False)
    
    def __str__(self):
        return f'نظر {self.author} در {self.article}'
    
    class Meta:
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')
        ordering = ['-created_at']


class Rating(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('article')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_ratings',
        verbose_name=_('user')
    )
    value = models.PositiveSmallIntegerField(
        _('value'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rating value between 1 and 5')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        unique_together = ('user', 'article')
        verbose_name = _('rating')
        verbose_name_plural = _('ratings')


class MediaCategory(models.Model):
    name = models.CharField(_('نام'), max_length=100)
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True)
    description = models.TextField(_('توضیحات'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='children', verbose_name=_('دسته‌بندی والد'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('دسته‌بندی رسانه')
        verbose_name_plural = _('دسته‌بندی‌های رسانه')
        ordering = ['name']


class BaseMedia(models.Model):
    STATUS_CHOICES = (
        ('draft', _('پیش‌نویس')),
        ('published', _('منتشر شده')),
        ('private', _('خصوصی')),
    )

    title = models.CharField(_('عنوان'), max_length=200)
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True)
    description = models.TextField(_('توضیحات'))
    thumbnail = models.ImageField(_('تصویر شاخص'), upload_to='media/thumbnails/', blank=True)
    category = models.ForeignKey(MediaCategory, on_delete=models.SET_NULL, null=True,
                                verbose_name=_('دسته‌بندی'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('برچسب‌ها'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              verbose_name=_('نویسنده'))
    
    status = models.CharField(_('وضعیت'), max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(_('ویژه'), default=False)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)
    published_at = models.DateTimeField(_('تاریخ انتشار'), null=True, blank=True)
    
    view_count = models.PositiveIntegerField(_('تعداد بازدید'), default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='%(class)s_likes',
                                  verbose_name=_('پسندها'))
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, 
                                     related_name='%(class)s_bookmarks',
                                     verbose_name=_('نشان‌شده‌ها'))
    
    # Add Generic Relations
    comments = GenericRelation('MediaComment')
    ratings = GenericRelation('MediaRating')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class Podcast(BaseMedia):
    audio_file = models.FileField(_('فایل صوتی'), upload_to='media/podcasts/')
    duration = models.DurationField(_('مدت زمان'))
    episode_number = models.PositiveIntegerField(_('شماره قسمت'), null=True, blank=True)
    season_number = models.PositiveIntegerField(_('شماره فصل'), null=True, blank=True)
    transcript = models.TextField(_('متن پیاده‌شده'), blank=True)
    
    class Meta:
        verbose_name = _('پادکست')
        verbose_name_plural = _('پادکست‌ها')


class Video(BaseMedia):
    VIDEO_TYPES = (
        ('youtube', 'یوتیوب'),
        ('vimeo', 'ویمیو'),
        ('upload', 'آپلود شده'),
        ('embedded', 'افلود شده'),

    )
    
    video_type = models.CharField(_('نوع ویدیو'), max_length=10, choices=VIDEO_TYPES, default='embedded')
    video_url = models.URLField(_('آدرس ویدیو'), blank=True, null=True)
    video_embed = models.TextField(_('امبد'), blank=True, null=True)

    video_file = models.FileField(_('فایل ویدیو'), upload_to='media/videos/', blank=True)
    duration = models.DurationField(_('مدت زمان'))
    is_premium = models.BooleanField(_('محتوای ویژه'), default=False)
    
    class Meta:
        verbose_name = _('ویدیو')
        verbose_name_plural = _('ویدیوها')


class File(BaseMedia):
    FILE_TYPES = (
        ('document', _('سند')),
        ('image', _('تصویر')),
        ('archive', _('آرشیو')),
        ('other', _('سایر')),
    )
    
    file = models.FileField(_('فایل'), upload_to='media/files/')
    file_type = models.CharField(_('نوع فایل'), max_length=10, choices=FILE_TYPES)
    file_size = models.PositiveIntegerField(_('حجم فایل'), help_text=_('حجم به بایت'))
    download_count = models.PositiveIntegerField(_('تعداد دانلود'), default=0)
    is_free = models.BooleanField(_('دانلود رایگان'), default=True)
    
    class Meta:
        verbose_name = _('فایل')
        verbose_name_plural = _('فایل‌ها')


class LiveStream(BaseMedia):
    STREAM_STATUS = (
        ('scheduled', _('برنامه‌ریزی شده')),
        ('live', _('در حال پخش')),
        ('ended', _('پایان یافته')),
        ('cancelled', _('لغو شده')),
    )
    
    stream_url = models.URLField(_('آدرس پخش'), blank=True)
    stream_key = models.CharField(_('کلید پخش'), max_length=100, blank=True)
    scheduled_start = models.DateTimeField(_('زمان شروع برنامه‌ریزی شده'))
    scheduled_end = models.DateTimeField(_('زمان پایان برنامه‌ریزی شده'), null=True, blank=True)
    actual_start = models.DateTimeField(_('زمان شروع واقعی'), null=True, blank=True)
    actual_end = models.DateTimeField(_('زمان پایان واقعی'), null=True, blank=True)
    stream_status = models.CharField(_('وضعیت پخش'), max_length=10, 
                                   choices=STREAM_STATUS, default='scheduled')
    is_recurring = models.BooleanField(_('پخش تکرار شونده'), default=False)
    max_viewers = models.PositiveIntegerField(_('حداکثر بازدیدکننده'), default=0)
    current_viewers = models.PositiveIntegerField(_('بازدیدکنندگان فعلی'), default=0)
    
    class Meta:
        verbose_name = _('پخش زنده')
        verbose_name_plural = _('پخش‌های زنده')


class MediaComment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='media_comments', verbose_name=_('نویسنده'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                              related_name='replies', verbose_name=_('نظر والد'))
    content = models.TextField(_('محتوا'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)
    is_approved = models.BooleanField(_('تایید شده'), default=False)
    
    def __str__(self):
        return f'نظر {self.author} در {self.content_object}'
    
    class Meta:
        verbose_name = _('نظر رسانه')
        verbose_name_plural = _('نظرات رسانه')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]


class MediaRating(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='media_ratings', verbose_name=_('کاربر'))
    value = models.PositiveSmallIntegerField(
        _('امتیاز'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('امتیاز بین 1 تا 5')
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)
    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        verbose_name = _('امتیاز رسانه')
        verbose_name_plural = _('امتیازهای رسانه')
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
