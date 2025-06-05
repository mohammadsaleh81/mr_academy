from django.urls import path, include
from rest_framework_nested import routers
from . import views


app_name = 'course'

urlpatterns = [

    # Tag URLs
    path('tags/', views.TagListCreateView.as_view(), name='tag-list'),
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('my-courses/', views.UserCoursesView.as_view(), name='user-courses'),

    # Course URLs
    path('courses/', views.CourseListCreateView.as_view(), name='course-list'),
    
    # Course enrollment - support both slug and ID
    path('courses/<slug:slug>/enroll/', views.CourseEnrollView.as_view(), name='course-enroll'),
    path('courses/<int:course_id>/enroll/', views.CourseEnrollView.as_view(), name='course-enroll-by-id'),
    
    # Course rating - support both slug and ID
    path('courses/<slug:slug>/rate/', views.CourseRateView.as_view(), name='course-rate'),
    path('courses/<int:course_id>/rate/', views.CourseRateView.as_view(), name='course-rate-by-id'),

    # Course detail - support both slug and ID
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/', views.CourseDetailView.as_view(), name='course-detail-by-id'),

    # Chapter URLs
    # path('courses/<slug:course_slug>/chapters/', views.ChapterListCreateView.as_view(), name='chapter-list'),
    # path('courses/<slug:course_slug>/chapters/<int:pk>/', views.ChapterDetailView.as_view(), name='chapter-detail'),

    # Lesson URLs
    # path('courses/<slug:course_slug>/chapters/<int:chapter_pk>/lessons/', views.LessonListCreateView.as_view(), name='lesson-list'),
    # path('courses/<slug:course_slug>/chapters/<int:chapter_pk>/lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    # path('courses/<slug:course_slug>/chapters/<int:chapter_pk>/lessons/<int:pk>/mark-complete/', views.LessonMarkCompleteView.as_view(), name='lesson-mark-complete'),
    # path('courses/<slug:course_slug>/chapters/<int:chapter_pk>/lessons/<int:pk>/update-progress/', views.LessonUpdateProgressView.as_view(), name='lesson-update-progress'),

    # Enrollment URLs
    # path('enrollments/', views.EnrollmentListV/iew.as_view(), name='enrollment-list'),

    # Discount URLs
    # path('discounts/', views.DiscountListCreateView.as_view(), name='discount-list'),
    # path('discounts/<int:pk>/', views.DiscountDetailView.as_view(), name='discount-detail'),
    # path('discounts/<int:pk>/validate/', views.DiscountValidateView.as_view(), name='discount-validate'),
    #
    # # LessonProgress URLs
    # path('lesson-progress/', views.LessonProgressListCreateView.as_view(), name='lesson-progress-list'),
    # path('lesson-progress/<int:pk>/', views.LessonProgressDetailView.as_view(), name='lesson-progress-detail'),
    # path('lesson-progress/<int:pk>/mark-completed/', views.LessonProgressMarkCompletedView.as_view(), name='lesson-progress-mark-completed'),
    # path('lesson-progress/<int:pk>/update-progress/', views.LessonProgressUpdateProgressView.as_view(), name='lesson-progress-update-progress'),

    # CourseProgress URL
    path('courses/<int:course_pk>/progress/', views.CourseProgressView.as_view(), name='course-progress'),

    # ChapterProgress URL
    path('courses/<int:course_pk>/chapter-progress/', views.ChapterProgressView.as_view(), name='chapter-progress'),

    # EnrollmentProgress URL
    path('courses/<int:course_pk>/enrollment-progress/', views.EnrollmentProgressView.as_view(), name='enrollment-progress'),

    # User Courses URL
]