import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count
from .models import Course

class CourseFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_free = django_filters.BooleanFilter(field_name='is_free')
    
    instructor = django_filters.CharFilter(field_name='instructor__username')
    level = django_filters.ChoiceFilter(choices=Course.LEVEL_CHOICES)
    
    tags = django_filters.CharFilter(field_name='tags__name', lookup_expr='icontains')
    
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    min_students = django_filters.NumberFilter(method='filter_min_students')
    
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Course
        fields = [
            'min_price', 'max_price', 'is_free',
            'instructor', 'level', 'tags',
            'min_rating', 'min_students',
            'created_after', 'created_before'
        ]

    def filter_min_rating(self, queryset, name, value):
        return queryset.annotate(
            avg_rating=Avg('ratings__rating')
        ).filter(avg_rating__gte=value)

    def filter_min_students(self, queryset, name, value):
        return queryset.annotate(
            student_count=Count('enrollments')
        ).filter(student_count__gte=value) 