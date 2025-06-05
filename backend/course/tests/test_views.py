import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from course.models import (
    Course, Chapter, Lesson, Discount, Enrollment,
    CourseRating, LessonProgress, Tag
)

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

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
def admin_user():
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
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
class TestCourseViewSet:
    def test_list_courses(self, api_client, course):
        url = reverse('course-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == course.title

    def test_retrieve_course(self, api_client, course):
        url = reverse('course-detail', kwargs={'slug': course.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == course.title

    def test_create_course_as_instructor(self, api_client, instructor):
        api_client.force_authenticate(user=instructor)
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description',
            'price': 150.00,
            'level': 'intermediate'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Course.objects.count() == 1

    def test_create_course_as_anonymous(self, api_client):
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description',
            'price': 150.00,
            'level': 'intermediate'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_enroll_in_course(self, api_client, course, user):
        api_client.force_authenticate(user=user)
        url = reverse('course-enroll', kwargs={'slug': course.slug})
        data = {'course_id': course.id}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Enrollment.objects.filter(user=user, course=course).exists()

    def test_rate_course(self, api_client, course, user):
        api_client.force_authenticate(user=user)
        url = reverse('course-rate', kwargs={'slug': course.slug})
        data = {'rating': 4, 'comment': 'Great course!'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert CourseRating.objects.filter(user=user, course=course).exists()

@pytest.mark.django_db
class TestChapterViewSet:
    def test_list_chapters(self, api_client, course, chapter):
        url = reverse('course-chapters-list', kwargs={'course_slug': course.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == chapter.title

    def test_create_chapter_as_instructor(self, api_client, course, instructor):
        api_client.force_authenticate(user=instructor)
        url = reverse('course-chapters-list', kwargs={'course_slug': course.slug})
        data = {
            'title': 'New Chapter',
            'description': 'New Description',
            'order': 2
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Chapter.objects.count() == 1

@pytest.mark.django_db
class TestLessonViewSet:
    def test_list_lessons(self, api_client, course, chapter, lesson):
        url = reverse('chapter-lessons-list', 
                     kwargs={'course_slug': course.slug, 'chapter_pk': chapter.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == lesson.title

    def test_mark_lesson_complete(self, api_client, course, chapter, lesson, user):
        api_client.force_authenticate(user=user)
        # First enroll the user
        Enrollment.objects.create(user=user, course=course, price_paid=course.price)
        
        url = reverse('chapter-lessons-mark-complete',
                     kwargs={
                         'course_slug': course.slug,
                         'chapter_pk': chapter.id,
                         'pk': lesson.id
                     })
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert LessonProgress.objects.filter(
            user=user,
            lesson=lesson,
            is_completed=True
        ).exists()

@pytest.mark.django_db
class TestDiscountViewSet:
    @pytest.fixture
    def discount(self, course):
        return Discount.objects.create(
            course=course,
            code='TEST10',
            percentage=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=10)
        )

    def test_create_discount_as_instructor(self, api_client, course, instructor, discount):
        api_client.force_authenticate(user=instructor)
        url = reverse('discount-list')
        data = {
            'course': course.id,
            'code': 'NEW20',
            'percentage': 20,
            'start_date': timezone.now().isoformat(),
            'end_date': (timezone.now() + timezone.timedelta(days=10)).isoformat()
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_validate_discount(self, api_client, course, instructor, discount):
        api_client.force_authenticate(user=instructor)
        url = reverse('discount-validate', kwargs={'pk': discount.id})
        data = {'course_id': course.id}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_valid'] is True

@pytest.mark.django_db
class TestEnrollmentViewSet:
    def test_list_enrollments(self, api_client, course, user):
        api_client.force_authenticate(user=user)
        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            price_paid=course.price
        )
        url = reverse('enrollment-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['course_title'] == course.title 