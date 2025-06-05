import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from course.models import (
    Course, Chapter, Lesson, Discount, Enrollment,
    CourseRating, LessonProgress, Tag
)

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def instructor():
    return User.objects.create_user(
        username='instructor',
        email='instructor@example.com',
        password='testpass123'
    )

@pytest.fixture
def course(instructor):
    return Course.objects.create(
        title='Test Course',
        description='Test Description',
        instructor=instructor,
        price=100.00,
        status='published',
        level='beginner'
    )

@pytest.fixture
def chapter(course):
    return Chapter.objects.create(
        course=course,
        title='Test Chapter',
        description='Test Description',
        order=1
    )

@pytest.fixture
def lesson(chapter):
    return Lesson.objects.create(
        chapter=chapter,
        title='Test Lesson',
        content='Test Content',
        content_type='video',
        video_url='https://example.com/video.mp4',
        duration=30,
        order=1
    )

@pytest.mark.django_db
class TestCourseModel:
    def test_course_creation(self, course):
        assert course.title == 'Test Course'
        assert course.slug == 'test-course'
        assert course.status == 'published'
        assert course.level == 'beginner'

    def test_course_str(self, course):
        assert str(course) == 'Test Course'

    def test_get_student_count(self, course, user):
        Enrollment.objects.create(
            user=user,
            course=course,
            price_paid=course.price
        )
        assert course.get_student_count() == 1

    def test_get_total_duration(self, course, chapter, lesson):
        assert course.get_total_duration() == 30

    def test_get_average_rating(self, course, user):
        CourseRating.objects.create(
            course=course,
            user=user,
            rating=4
        )
        assert course.get_average_rating() == 4.0

@pytest.mark.django_db
class TestChapterModel:
    def test_chapter_creation(self, chapter):
        assert chapter.title == 'Test Chapter'
        assert chapter.order == 1

    def test_chapter_str(self, chapter):
        assert str(chapter) == f"{chapter.course.title} - فصل 1: Test Chapter"

    def test_get_duration(self, chapter, lesson):
        assert chapter.get_duration() == 30

@pytest.mark.django_db
class TestLessonModel:
    def test_lesson_creation(self, lesson):
        assert lesson.title == 'Test Lesson'
        assert lesson.content_type == 'video'
        assert lesson.duration == 30

    def test_lesson_str(self, lesson):
        assert str(lesson) == f"{lesson.chapter.course.title} - {lesson.chapter.title} - درس 1: Test Lesson"

    def test_lesson_validation(self, chapter):
        with pytest.raises(ValidationError):
            lesson = Lesson(
                chapter=chapter,
                title='Invalid Lesson',
                content='Test Content',
                content_type='video',
                order=1
            )
            lesson.full_clean()

@pytest.mark.django_db
class TestDiscountModel:
    @pytest.fixture
    def discount(self, course):
        return Discount.objects.create(
            course=course,
            code='TEST10',
            percentage=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

    def test_discount_creation(self, discount):
        assert discount.code == 'TEST10'
        assert discount.percentage == 10

    def test_discount_validation(self, course):
        # Test invalid dates
        with pytest.raises(ValidationError):
            discount = Discount(
                course=course,
                code='TEST10',
                percentage=10,
                start_date=timezone.now(),
                end_date=timezone.now() - timezone.timedelta(days=1)
            )
            discount.full_clean()

    def test_discount_is_valid(self, discount, course):
        is_valid, message = discount.is_valid(course)
        assert is_valid is True

        # Test expired discount
        discount.end_date = timezone.now() - timezone.timedelta(days=1)
        discount.save()
        is_valid, message = discount.is_valid(course)
        assert is_valid is False

@pytest.mark.django_db
class TestEnrollmentModel:
    def test_enrollment_creation(self, course, user):
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            price_paid=course.price
        )
        assert enrollment.status == 'active'
        assert enrollment.price_paid == course.price

    def test_get_progress_percentage(self, course, user, chapter, lesson):
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            price_paid=course.price
        )
        
        # No progress yet
        assert enrollment.get_progress_percentage() == 0
        
        # Complete one lesson
        LessonProgress.objects.create(
            user=user,
            lesson=lesson,
            is_completed=True
        )
        assert enrollment.get_progress_percentage() == 100

@pytest.mark.django_db
class TestLessonProgressModel:
    def test_lesson_progress_creation(self, lesson, user):
        progress = LessonProgress.objects.create(
            user=user,
            lesson=lesson,
            watched_duration=15
        )
        assert progress.is_completed is False
        assert progress.watched_duration == 15

    def test_mark_completed(self, course, user, chapter, lesson):
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            price_paid=course.price
        )
        
        progress = LessonProgress.objects.create(
            user=user,
            lesson=lesson
        )
        
        progress.mark_completed()
        assert progress.is_completed is True
        
        # Refresh enrollment from db
        enrollment.refresh_from_db()
        assert enrollment.status == 'completed' 