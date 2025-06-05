from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (Category, Tag, Article, Comment, Rating, ArticleLike, ArticleBookmark,
                    MediaCategory, Podcast, Video, File, LiveStream, MediaComment, MediaRating)
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
# Removed custom filter imports as they're not available in this version


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'article_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    # Unfold enhancements
    icon = "folder"
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    # Add fieldsets for Category
    fieldsets = (
        (_('Category Information'), {
            'fields': ('name', 'slug', 'description'),
            'classes': ('tab',),
        }),

    )
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _('Articles')


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'article_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    # Unfold enhancements
    icon = "tag"
    list_per_page = 30
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = _('Articles')


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    tab = True
    tab_title = _("Comments")
    tab_icon = "chat"
    verbose_name = _("Comment")
    verbose_name_plural = _("Comments")
    fields = ('author', 'content', 'created_at', 'is_approved')
    readonly_fields = ('created_at', 'content','author', )
    can_delete = True
    show_change_link = True
    classes = ('collapse-entry',)


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ('title', 'author', 'category', 'status',
                   'like_count', 'bookmark_count', 'view_count', 'created_at')
    list_filter = ('status', 'category', 'tags', 'created_at')
    search_fields = ('title', 'content', 'author__phone_number', 'author__first_name', 
                    'author__last_name')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    autocomplete_fields = ('category', 'tags')
    readonly_fields = ('created_at', 'updated_at', 'view_count',
                      'like_count', 'bookmark_count')
    inlines = [CommentInline]
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'content', 'summary', 'featured_image', 'thumbnail'),
            'classes': ('tab',)

        }),
        (_('Publishing'), {
            'fields': ('author', 'category', 'tags', 'status', 'published_at'),
            'classes': ('tab',)

        }),
        (_('Statistics'), {
            'fields': ('view_count', 'like_count', 'bookmark_count'),
            'classes': ('tab',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',)
        }),
    )
    

    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = _('Likes')
    
    def bookmark_count(self, obj):
        return obj.bookmarks.count()
    bookmark_count.short_description = _('Bookmarks')


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('article', 'author', 'short_content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__phone_number', 'article__title')
    raw_id_fields = ('article', 'author', 'parent')
    actions = ['approve_comments', 'unapprove_comments']
    
    # Unfold enhancements
    icon = "chat"
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Comment Details'), {
            'fields': ('article', 'parent', 'author', 'content', 'is_approved'),
            'classes': ('tab',),
            'tab_icon': 'comment'
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('tab',),
            'tab_icon': 'schedule'
        }),
    )
    
    def short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    short_content.short_description = _('Content')
    
    @admin.action(description=_('Approve selected comments'))
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f'{updated} comments have been approved.'))
    
    @admin.action(description=_('Unapprove selected comments'))
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(f'{updated} comments have been unapproved.'))


@admin.register(Rating)
class RatingAdmin(ModelAdmin):
    list_display = ('article', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('article__title', 'user__phone_number')
    raw_id_fields = ('article', 'user')
    
    # Unfold enhancements
    icon = "star"
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Rating Details'), {
            'fields': ('article', 'user', 'value'),
            'classes': ('tab',),
            'tab_icon': 'grade'
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('tab',),
            'tab_icon': 'schedule'
        }),
    )


class MediaCommentInline(GenericTabularInline):
    model = MediaComment
    extra = 0
    fields = ('author', 'content', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True
    show_change_link = True

    # Unfold enhancements
    tab = True
    tab_title = _("Comments")
    tab_icon = "chat"
    verbose_name = _("Comment")
    verbose_name_plural = _("Comments")
    classes = ('collapse-entry',)


class MediaRatingInline(GenericTabularInline):
    model = MediaRating
    extra = 0
    fields = ('user', 'value', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True
    
    # Unfold enhancements
    tab = True
    tab_title = _("Ratings")
    tab_icon = "star"
    verbose_name = _("Rating")
    verbose_name_plural = _("Ratings")
    classes = ('collapse-entry',)


@admin.register(MediaCategory)
class MediaCategoryAdmin(ModelAdmin):
    list_display = ('name', 'parent', 'get_children_count', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    # Unfold enhancements
    icon = "folder_special"
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Category Details'), {
            'fields': ('name', 'slug', 'description', 'parent'),
            'classes': ('tab',),
            'tab_icon': 'category'
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('tab',),
            'tab_icon': 'schedule'
        }),
    )
    
    def get_children_count(self, obj):
        return obj.children.count()
    get_children_count.short_description = _('Subcategories')


class BaseMediaAdmin(ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'featured',
                   'view_count', 'get_likes_count', 'get_bookmarks_count', 'created_at')
    list_filter = ('status', 'featured', 'category', 'tags', 'created_at')
    search_fields = ('title', 'description', 'author__phone_number')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    autocomplete_fields = ('category', 'tags')
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    inlines = [MediaCommentInline, MediaRatingInline]
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = _('Likes')
    
    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()
    get_bookmarks_count.short_description = _('Bookmarks')


@admin.register(Podcast)
class PodcastAdmin(BaseMediaAdmin):
    # Unfold enhancements
    icon = "podcasts"
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'description', 'thumbnail', 'audio_file', 'transcript'),
            'classes': ('tab',),
        }),
        (_('Episode Info'), {
            'fields': ('duration', 'episode_number', 'season_number'),
            'classes': ('tab',),
        }),
        (_('Publishing'), {
            'fields': ('author', 'category', 'tags', 'status', 'featured', 'published_at'),
            'classes': ('tab',),
        }),
        (_('Statistics'), {
            'fields': ('view_count',),
            'classes': ('tab',),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )

# https://api.gport.sbs/
@admin.register(Video)
class VideoAdmin(BaseMediaAdmin):
    # Unfold enhancements
    icon = "videocam"
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'description', 'thumbnail'),
            'classes': ('tab',),
        }),
        (_('Video'), {
            'fields': ('video_type', 'video_url', 'video_file', 'duration', 'is_premium'),
            'classes': ('tab',),
        }),
        (_('Publishing'), {
            'fields': ('author', 'category', 'tags', 'status', 'featured', 'published_at'),
            'classes': ('tab',),
        }),
        (_('Statistics'), {
            'fields': ('view_count',),
            'classes': ('tab',),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )
    list_filter = BaseMediaAdmin.list_filter + ('is_premium', 'video_type')


@admin.register(File)
class FileAdmin(BaseMediaAdmin):
    # Unfold enhancements
    icon = "insert_drive_file"
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'description', 'thumbnail'),
            'classes': ('tab',),
        }),
        (_('File'), {
            'fields': ('file', 'file_type', 'file_size', 'is_free'),
            'classes': ('tab',),
        }),
        (_('Publishing'), {
            'fields': ('author', 'category', 'tags', 'status', 'featured', 'published_at'),
            'classes': ('tab',),
        }),
        (_('Statistics'), {
            'fields': ('view_count', 'download_count'),
            'classes': ('tab',),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
        }),
    )
    readonly_fields = BaseMediaAdmin.readonly_fields + ('file_size', 'download_count')
    list_filter = BaseMediaAdmin.list_filter + ('is_free', 'file_type')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only on creation
            obj.file_size = obj.file.size
        super().save_model(request, obj, form, change)


@admin.register(LiveStream)
class LiveStreamAdmin(BaseMediaAdmin):
    # Unfold enhancements
    icon = "live_tv"
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'description', 'thumbnail'),
            'classes': ('tab',),
            'tab_icon': 'description'
        }),
        (_('Stream Details'), {
            'fields': ('stream_url', 'stream_key', 'stream_status', 'is_recurring'),
            'classes': ('tab',),
            'tab_icon': 'settings_input_antenna'
        }),
        (_('Schedule'), {
            'fields': ('scheduled_start', 'scheduled_end', 'actual_start', 'actual_end'),
            'classes': ('tab',),
            'tab_icon': 'event'
        }),
        (_('Publishing'), {
            'fields': ('author', 'category', 'tags', 'status', 'featured'),
            'classes': ('tab',),
            'tab_icon': 'publish'
        }),
        (_('Statistics'), {
            'fields': ('view_count', 'max_viewers', 'current_viewers'),
            'classes': ('tab',),
            'tab_icon': 'analytics'
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('tab',),
            'tab_icon': 'schedule'
        }),
    )
    readonly_fields = BaseMediaAdmin.readonly_fields + ('max_viewers', 'current_viewers')
    list_filter = BaseMediaAdmin.list_filter + ('stream_status', 'is_recurring')
    list_display = BaseMediaAdmin.list_display + ('stream_status', 'scheduled_start')


@admin.register(MediaComment)
class MediaCommentAdmin(ModelAdmin):
    list_display = ('content_object', 'author', 'short_content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__phone_number')
    raw_id_fields = ('author', 'parent')
    actions = ['approve_comments', 'unapprove_comments']
    
    # Unfold enhancements
    icon = "comment"
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Comment Details'), {
            'fields': ('content_type', 'object_id', 'parent', 'author', 'content', 'is_approved'),
            'classes': ('tab',),
            'tab_icon': 'chat'
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('tab',),
            'tab_icon': 'schedule'
        }),
    )
    
    def short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    short_content.short_description = _('Content')
    
    @admin.action(description=_('Approve selected comments'))
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, _(f'{updated} comments have been approved.'))
    
    @admin.action(description=_('Unapprove selected comments'))
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, _(f'{updated} comments have been unapproved.'))
