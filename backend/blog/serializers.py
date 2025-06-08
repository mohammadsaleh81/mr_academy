from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import (
    Article, Video, Podcast, Tag, Category, MediaCategory,
    Comment, MediaComment, ArticleLike, ArticleBookmark
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class MediaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaCategory
        fields = ['id', 'name', 'slug', 'description']

class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    published = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    tags = TagSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'summary', 'thumbnail',
            'author', 'category', 'tags', 'published', 'view_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'view_count']

    def get_author(self, obj):
        return obj.author.first_name + ' ' + obj.author.last_name

    def get_published(self, obj):
        return obj.published_at.strftime('%Y-%m-%d') if obj.published_at else None


    def get_thumbnail(self, obj):
        return 'https://api.gport.sbs' + obj.thumbnail.url if obj.thumbnail else ''

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        category_data = validated_data.pop('category', None)
        
        # Get or create category
        if category_data:
            category, _ = Category.objects.get_or_create(**category_data)
            validated_data['category'] = category
        
        # Create article
        article = Article.objects.create(**validated_data)
        
        # Add tags
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            article.tags.add(tag)
        
        return article

class VideoSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    category = MediaCategorySerializer()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'video_type', 'video_embed','video_url', 'duration',
            'is_premium', 'author', 'category', 'tags', 'status',
            'featured', 'created_at', 'updated_at', 'published_at',
            'view_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'view_count']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else None


    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        category_data = validated_data.pop('category', None)
        
        # Get or create category
        if category_data:
            category, _ = MediaCategory.objects.get_or_create(**category_data)
            validated_data['category'] = category
        
        # Create video
        video = Video.objects.create(**validated_data)
        
        # Add tags
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            video.tags.add(tag)
        
        return video

class PodcastSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    category = MediaCategorySerializer()
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Podcast
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'audio_file', 'duration', 'episode_number', 'season_number',
            'transcript', 'author', 'category', 'tags', 'status',
            'featured', 'created_at', 'updated_at', 'published_at',
            'view_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'view_count']

        
    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else None

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        category_data = validated_data.pop('category', None)
        
        # Get or create category
        if category_data:
            category, _ = MediaCategory.objects.get_or_create(**category_data)
            validated_data['category'] = category
        
        # Create podcast
        podcast = Podcast.objects.create(**validated_data)
        
        # Add tags
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            podcast.tags.add(tag)
        
        return podcast

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())
    created_at = serializers.SerializerMethodField()


    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'author', 'parent', 'content',
            'created_at', 'updated_at', 'is_approved', 'replies'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_approved', 'replies']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else None

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    def validate_parent(self, value):
        if value:
            if value.parent:
                raise serializers.ValidationError("نظر نمی‌تواند بیش از یک سطح پاسخ داشته باشد.")
            if value.article_id != self.initial_data.get('article'):
                raise serializers.ValidationError("پاسخ باید به نظری از همان مقاله باشد.")
        return value

class MediaCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    content_object_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaComment
        fields = [
            'id', 'content_type', 'object_id', 'content_object_name', 'author', 'parent',
            'content', 'created_at', 'updated_at', 'is_approved', 'replies'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_approved', 'replies', 'content_object_name']

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d') if obj.created_at else None

    def get_replies(self, obj):
        if obj.replies.exists():
            return MediaCommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []
    
    def get_content_object_name(self, obj):
        if obj.content_object:
            return str(obj.content_object)
        return None

    def validate(self, data):
        try:
            content_type = data['content_type']
            object_id = data['object_id']
            content_type.get_object_for_this_type(id=object_id)
        except (ContentType.DoesNotExist, AttributeError):
            raise serializers.ValidationError("Invalid content type or object ID")
        return data

    def validate_parent(self, value):
        if value:
            if value.parent:
                raise serializers.ValidationError("نظر نمی‌تواند بیش از یک سطح پاسخ داشته باشد.")
            # بررسی اینکه parent comment مربوط به همان محتوا باشد
            if (value.content_type_id != self.initial_data.get('content_type') or
                value.object_id != self.initial_data.get('object_id')):
                raise serializers.ValidationError("پاسخ باید به نظری از همان محتوا باشد.")
        return value

# سریالایزر ساده برای ایجاد کامنت رسانه که نیاز به کمتر اطلاعات دارد
class MediaCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaComment
        fields = ['content_type', 'object_id', 'parent', 'content']
    
    def validate(self, data):
        try:
            content_type = data['content_type']
            object_id = data['object_id']
            content_object = content_type.get_object_for_this_type(id=object_id)
            
            # بررسی اینکه محتوا منتشر شده باشد
            if hasattr(content_object, 'status') and content_object.status != 'published':
                raise serializers.ValidationError("نمی‌توان برای محتوای منتشر نشده کامنت گذاشت.")
                
        except (ContentType.DoesNotExist, AttributeError):
            raise serializers.ValidationError("نوع محتوا یا شناسه محتوا نامعتبر است.")
        return data

    def validate_parent(self, value):
        if value:
            if value.parent:
                raise serializers.ValidationError("نظر نمی‌تواند بیش از یک سطح پاسخ داشته باشد.")
            # بررسی اینکه parent comment مربوط به همان محتوا باشد
            if (value.content_type_id != self.initial_data.get('content_type') or
                value.object_id != self.initial_data.get('object_id')):
                raise serializers.ValidationError("پاسخ باید به نظری از همان محتوا باشد.")
        return value

class ArticleLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())

    class Meta:
        model = ArticleLike
        fields = ['id', 'user', 'article', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user:
            raise serializers.ValidationError("Authentication required.")
        
        user = request.user
        article = data['article']
        
        if ArticleLike.objects.filter(user=user, article=article).exists():
            raise serializers.ValidationError("You have already liked this article.")
        return data

class ArticleBookmarkSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())

    class Meta:
        model = ArticleBookmark
        fields = ['id', 'user', 'article', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user:
            raise serializers.ValidationError("Authentication required.")
        
        user = request.user
        article = data['article']
        
        if ArticleBookmark.objects.filter(user=user, article=article).exists():
            raise serializers.ValidationError("You have already bookmarked this article.")
        return data 