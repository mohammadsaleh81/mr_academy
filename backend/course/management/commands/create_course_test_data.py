from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from course.models import Course, Chapter, Lesson, Discount, Enrollment
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates test data for courses, chapters, lessons, discounts, and enrollments'

    def create_test_users(self):
        # Create test instructors
        instructors = []
        for i in range(3):
            instructor, created = User.objects.get_or_create(
                email=f'instructor{i+1}@example.com',
                defaults={
                    'is_staff': True,
                    'is_active': True,
                    'phone_number': f'0911{str(i+1).zfill(7)}',  # Generate unique phone numbers
                }
            )
            if created:
                instructor.set_password('123456')
                instructor.save()
            instructors.append(instructor)

        # Create test students
        students = []
        for i in range(5):
            student, created = User.objects.get_or_create(
                email=f'student{i+1}@example.com',
                defaults={
                    'is_active': True,
                    'phone_number': f'0912{str(i+1).zfill(7)}',  # Generate unique phone numbers
                }
            )
            if created:
                student.set_password('123456')
                student.save()
            students.append(student)

        return instructors, students

    def create_test_courses(self, instructors):
        courses = []
        course_titles = [
            'Python Programming Fundamentals',
            'Web Development with Django',
            'Machine Learning Basics',
            'Data Science Essentials',
            'JavaScript for Beginners',
            'React.js Advanced Concepts',
        ]

        for title in course_titles:
            course = Course.objects.create(
                title=title,
                description=f'Comprehensive course on {title}. Learn everything from basics to advanced concepts.',
                instructor=random.choice(instructors),
                price=random.choice([0, 29.99, 49.99, 99.99]),
                is_free=random.choice([True, False]),
                # is_published=random.choice([True, False])
            )
            courses.append(course)

        return courses

    def create_test_chapters(self, courses):
        chapters = []
        for course in courses:
            num_chapters = random.randint(3, 6)
            for i in range(num_chapters):
                chapter = Chapter.objects.create(
                    course=course,
                    title=f'Chapter {i+1}: {random.choice(["Introduction", "Basics", "Advanced Topics", "Practice Projects", "Final Project"])}',
                    description=f'Detailed coverage of important concepts in Chapter {i+1}',
                    order=i+1
                )
                chapters.append(chapter)

        return chapters

    def create_test_lessons(self, chapters):
        lessons = []
        for chapter in chapters:
            num_lessons = random.randint(3, 5)
            for i in range(num_lessons):
                lesson = Lesson.objects.create(
                    chapter=chapter,
                    title=f'Lesson {i+1}: {random.choice(["Theory", "Practice", "Quiz", "Project", "Review"])}',
                    content=f'Detailed content for lesson {i+1} in {chapter.title}',
                    video_url=f'https://example.com/videos/lesson-{random.randint(1, 1000)}',
                    duration=random.randint(10, 60),
                    order=i+1,
                    is_free_preview=random.choice([True, False])
                )
                lessons.append(lesson)

        return lessons

    def create_test_discounts(self, courses):
        discounts = []
        for course in courses:
            if random.choice([True, False]):
                now = timezone.now()
                discount = Discount.objects.create(
                    course=course,
                    code=f'DISC{random.randint(1000, 9999)}',
                    percentage=random.choice([10, 20, 30, 40, 50]),
                    start_date=now,
                    end_date=now + timedelta(days=random.randint(7, 30)),
                    is_active=True,
                    max_uses=random.randint(10, 100),
                    current_uses=0
                )
                discounts.append(discount)

        return discounts

    def create_test_enrollments(self, courses, students, discounts):
        enrollments = []
        for student in students:
            num_enrollments = random.randint(1, 3)
            available_courses = list(courses)
            random.shuffle(available_courses)
            
            for course in available_courses[:num_enrollments]:
                course_discounts = [d for d in discounts if d.course == course]
                discount_used = random.choice(course_discounts) if course_discounts else None
                
                price_paid = 0 if course.is_free else course.price
                if discount_used and not course.is_free:
                    price_paid = price_paid * (1 - discount_used.percentage / 100)

                enrollment = Enrollment.objects.create(
                    user=student,
                    course=course,
                    price_paid=price_paid,
                    discount_used=discount_used
                )
                
                if discount_used:
                    discount_used.current_uses += 1
                    discount_used.save()
                
                enrollments.append(enrollment)

        return enrollments

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        try:
            # Create test users
            self.stdout.write('Creating test users...')
            instructors, students = self.create_test_users()

            # Create test courses
            self.stdout.write('Creating test courses...')
            courses = self.create_test_courses(instructors)

            # Create test chapters
            self.stdout.write('Creating test chapters...')
            chapters = self.create_test_chapters(courses)

            # Create test lessons
            self.stdout.write('Creating test lessons...')
            lessons = self.create_test_lessons(chapters)

            # Create test discounts
            self.stdout.write('Creating test discounts...')
            discounts = self.create_test_discounts(courses)

            # Create test enrollments
            self.stdout.write('Creating test enrollments...')
            enrollments = self.create_test_enrollments(courses, students, discounts)

            self.stdout.write(self.style.SUCCESS('Successfully created test data!'))
            self.stdout.write(f'''
Summary:
- {len(instructors)} instructors created
- {len(students)} students created
- {len(courses)} courses created
- {len(chapters)} chapters created
- {len(lessons)} lessons created
- {len(discounts)} discounts created
- {len(enrollments)} enrollments created

Test Users:
Instructors: instructor1@example.com (0911{str(1).zfill(7)}), instructor2@example.com (0911{str(2).zfill(7)}), instructor3@example.com (0911{str(3).zfill(7)})
Students: student1@example.com (0912{str(1).zfill(7)}), student2@example.com (0912{str(2).zfill(7)}), student3@example.com (0912{str(3).zfill(7)}), student4@example.com (0912{str(4).zfill(7)}), student5@example.com (0912{str(5).zfill(7)})
Password for all users: 123456
''')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test data: {str(e)}'))
            raise 