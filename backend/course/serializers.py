from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from .models import (
    Course, Chapter, Lesson, Discount, Enrollment,
    CourseRating, LessonProgress, Tag, Comment, CourseProgress
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'email','thumbnail')


    def get_thumbnail(self, obj):
        path =  obj.avatar.url if obj.avatar else '/media/user.png'
        return  'https://api.gport.sbs' + path
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class LessonProgressSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    chapter_title = serializers.CharField(source='lesson.chapter.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'chapter_title',
            'status', 'status_display', 'is_completed',
            'watched_duration', 'last_position', 'completion_date',
            'last_activity', 'notes', 'rating'
        ]
        read_only_fields = ['completion_date', 'last_activity']

    def validate_rating(self, value):
        if value and not self.instance.is_completed:
            raise serializers.ValidationError(_('برای امتیازدهی باید درس را تکمیل کرده باشید.'))
        return value

class LessonProgressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['watched_duration', 'last_position', 'notes']

    def validate(self, data):
        if 'watched_duration' in data:
            lesson_duration = self.instance.lesson.duration
            if lesson_duration and data['watched_duration'] > lesson_duration:
                raise serializers.ValidationError(
                    _('مدت زمان مشاهده شده نمی‌تواند از مدت زمان درس بیشتر باشد.')
                )
        return data

class LessonSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'chapter', 'title', 'content', 'content_type',
            'video_url', 'duration', 'order', 'is_free_preview',
            'points', 'progress'
        ]

    def get_progress(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            progress = obj.progress.filter(user=user).first()
            if progress:
                return LessonProgressSerializer(progress).data
        return None

class ChapterSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    total_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = ['id', 'course', 'title', 'description', 'order', 'lessons', 'total_duration']

    def get_total_duration(self, obj):
        return obj.get_duration()

class CourseRatingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = CourseRating
        fields = ['id', 'course', 'user_email', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'id', 'course', 'code', 'percentage', 'start_date',
            'end_date', 'is_active', 'max_uses', 'current_uses',
            'min_course_price'
        ]

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                _('تاریخ شروع باید قبل از تاریخ پایان باشد.')
            )
        return data

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    progress_percentage = serializers.FloatField(source='get_progress_percentage', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'course', 'course_title', 'price_paid',
            'discount_used', 'status', 'created_at', 'completion_date',
            'progress_percentage'
        ]
        read_only_fields = ['user', 'status', 'completion_date']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    rating_avg = serializers.FloatField(source='get_average_rating', read_only=True)
    student_count = serializers.IntegerField(source='get_student_count', read_only=True)
    total_duration = serializers.IntegerField(source='get_total_duration', read_only=True)
    created = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'instructor_name', 'thumbnail',
            'price', 'is_free', 'status', 'level', 'tags',
            'rating_avg', 'student_count', 'total_duration',
            'created', 'is_enrolled', 'progress_percentage'
        ]

    def get_thumbnail(self, obj):
        return  'https://api.gport.sbs' + obj.thumbnail.url

    def get_created(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=request.user, course=obj).first()
            if enrollment:
                course_progress = CourseProgress(request.user, obj)
                return course_progress.completion_percentage
        return 0

class CourseInfoSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    total_chapters = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description',
            'instructor', 'price', 'created_at',
            'updated_at', 'status', 'level', 'tags',
            'total_students', 'total_duration',
            'average_rating', 'total_chapters',
            'total_lessons', 'thumbnail', 'is_enrolled',
            'progress_percentage'
        ]

    def get_thumbnail(self, obj):
        return 'https://api.gport.sbs' + obj.thumbnail.url
    def get_total_students(self, obj):
        return obj.get_student_count()

    def get_price(self, obj):
        return int(obj.price)

    def get_total_chapters(self, obj):
        return obj.get_total_chapters()

    def get_total_lessons(self, obj):
        return obj.get_total_lessons()

    def get_total_duration(self, obj):
        return obj.get_total_duration()

    def get_instructor(self, obj):
        obj.instructor.last_name = 'صالحی'
        obj.instructor.first_name = 'محمد'
        obj.instructor.save()
        return obj.instructor.first_name + ' ' + obj.instructor.last_name

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=request.user, course=obj).first()
            if enrollment:
                course_progress = CourseProgress(request.user, obj)
                return course_progress.completion_percentage
        return 0

    def get_average_rating(self, obj):
        return obj.get_average_rating()

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    replies = serializers.SerializerMethodField()

    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'user','content', 'replies','created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

    def validate_parent(self, value):
        if value:
            if value.parent:
                raise serializers.ValidationError("نظر نمی‌تواند بیش از یک سطح پاسخ داشته باشد.")
            if value.article_id != self.initial_data.get('article'):
                raise serializers.ValidationError("پاسخ باید به نظری از همان مقاله باشد.")
        return value

    def get_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
class CourseDetailSerializer(serializers.Serializer):
    info = CourseInfoSerializer()
    chapters = ChapterSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, required=False)

class CourseEnrollSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    discount_code = serializers.CharField(required=False, allow_blank=True)

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(id=value, status='published')
            if course.enrollments.filter(user=self.context['request'].user).exists():
                raise serializers.ValidationError(_('شما قبلاً در این دوره ثبت‌نام کرده‌اید.'))
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError(_('دوره مورد نظر یافت نشد.'))

    def validate_discount_code(self, value):
        if not value:
            return None
            
        try:
            course_id = self.initial_data.get('course_id')
            course = Course.objects.get(id=course_id)
            discount = Discount.objects.get(code=value, course=course)
            
            is_valid, message = discount.is_valid(course)
            if not is_valid:
                raise serializers.ValidationError(message)
                
            return discount
        except Discount.DoesNotExist:
            raise serializers.ValidationError(_('کد تخفیف نامعتبر است.'))

    def validate(self, data):
        from user.models import WalletTransaction
        
        user = self.context['request'].user
        course = Course.objects.get(id=data['course_id'])
        discount = data.get('discount_code')
        
        # Calculate final price
        price = course.price
        if discount:
            price = price * (1 - discount.percentage / 100)
        
        # For paid courses, check wallet balance
        if price > 0:
            if user.wallet_balance < price:
                raise serializers.ValidationError(
                    _('موجودی کیف پول شما برای خرید این دوره کافی نیست. '
                      f'موجودی فعلی: {user.wallet_balance:,.0f} تومان، '
                      f'قیمت دوره: {price:,.0f} تومان')
                )
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        from user.models import WalletTransaction
        
        user = self.context['request'].user
        course = Course.objects.get(id=validated_data['course_id'])
        discount = validated_data.get('discount_code')
        
        # Calculate final price
        price = course.price
        if discount:
            price = price * (1 - discount.percentage / 100)
            
        # Process payment if course is not free
        if price > 0:
            # Deduct from user wallet
            user.deduct_from_wallet(price)
            
            # Create wallet transaction
            WalletTransaction.objects.create(
                user=user,
                amount=price,
                transaction_type='purchase',
                description=f'خرید دوره: {course.title}',
                status='completed'
            )
            
        # Create enrollment
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            price_paid=price,
            discount_used=discount
        )
        
        # Update discount usage if applicable
        if discount:
            discount.current_uses += 1
            discount.save()
        
        return enrollment

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'instructor',
            'thumbnail', 'price', 'is_free', 'created_at',
            'updated_at', 'is_published', 'chapters'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        return Course.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CourseProgressSerializer(serializers.Serializer):
    completion_percentage = serializers.FloatField()
    completed_lessons = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    in_progress_lessons = serializers.IntegerField()
    watched_duration = serializers.IntegerField()
    total_duration = serializers.IntegerField()
    time_spent_percentage = serializers.FloatField()
    last_activity = serializers.DateTimeField()

class ChapterProgressSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    lessons_progress = LessonProgressSerializer(many=True, source='lessons__progress', read_only=True)
    
    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'order', 'progress_percentage',
            'lessons_progress'
        ]

    def get_progress_percentage(self, obj):
        print(self.context)
        print("0000000000000")
        user = self.context['user']
        course_progress = CourseProgress(user, obj.course)
        return course_progress.get_chapter_progress(obj)

class EnrollmentDetailSerializer(EnrollmentSerializer):
    progress = CourseProgressSerializer(source='progress_metrics', read_only=True)
    chapters_progress = ChapterProgressSerializer(
        many=True,
        source='course.chapters',
        read_only=True
    )
    next_lesson = serializers.SerializerMethodField()

    class Meta(EnrollmentSerializer.Meta):
        fields = EnrollmentSerializer.Meta.fields + [
            'progress', 'chapters_progress', 'next_lesson'
        ]

    def get_next_lesson(self, obj):
        course_progress = CourseProgress(obj.user, obj.course)
        next_lesson = course_progress.get_next_lesson()
        if next_lesson:
            return {
                'id': next_lesson.id,
                'title': next_lesson.title,
                'chapter': next_lesson.chapter.title,
                'order': next_lesson.order
            }
        return None