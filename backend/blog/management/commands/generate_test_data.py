import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker
from blog.models import Category, Tag, Article, Comment, Rating, MediaCategory, Podcast, Video, File, LiveStream
from course.models import Course, Chapter, Lesson, Discount, Enrollment

User = get_user_model()
fake = Faker(['fa_IR', 'en_US'])

class Command(BaseCommand):
    help = 'Generates test data for Master Trader Academy'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting test data generation for Master Trader Academy...')
        
        # Create test users
        self.create_users()
        
        # Create blog related data
        self.create_categories()
        self.create_tags()
        self.create_articles()
        
        # Create media related data
        self.create_media_categories()
        self.create_media_content()
        
        # Create course related data
        self.create_courses()
        
        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))

    def create_users(self):
        self.stdout.write('Creating users...')
        # Create superuser and main instructor
        if not User.objects.filter(phone_number='09123456789').exists():
            User.objects.create_superuser(
                phone_number='09123456789',
                password='admin123',
                first_name='مسعود',
                last_name='مستر تریدر',
                email='admin@mastertrader.academy',
                is_phone_verified=True
            )

        # Create other instructors
        instructors = [
            ('علی', 'تحلیلگر', '09121111111'),
            ('محمد', 'ترید‌گر', '09122222222'),
            ('رضا', 'کریپتوکار', '09123333333'),
        ]
        
        for fname, lname, phone in instructors:
            if not User.objects.filter(phone_number=phone).exists():
                User.objects.create_user(
                    phone_number=phone,
                    password='user123',
                    first_name=fname,
                    last_name=lname,
                    email=f'{fname}@mastertrader.academy',
                    is_staff=True,
                    is_phone_verified=True
                )

        # Create regular users
        for i in range(20):
            phone = f'091{random.randint(10000000, 99999999)}'
            if not User.objects.filter(phone_number=phone).exists():
                User.objects.create_user(
                    phone_number=phone,
                    password='user123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    is_phone_verified=True
                )

    def create_categories(self):
        self.stdout.write('Creating categories...')
        categories = [
            'تحلیل تکنیکال',
            'تحلیل فاندامنتال',
            'ارزهای دیجیتال',
            'روانشناسی بازار',
            'مدیریت سرمایه',
            'استراتژی‌های معاملاتی',
            'بازارهای مالی',
            'بلاکچین'
        ]
        for cat_name in categories:
            slug = slugify(cat_name)
            if not Category.objects.filter(slug=slug).exists():
                Category.objects.create(
                    name=cat_name,
                    slug=slug,
                    description=fake.paragraph()
                )

    def create_tags(self):
        self.stdout.write('Creating tags...')
        tags = [
            'بیت‌کوین', 'اتریوم', 'آلت‌کوین', 'NFT', 
            'DeFi', 'متاورس', 'وب3', 'استیکینگ',
            'فارمینگ', 'ترید', 'هولد', 'نوسان‌گیری',
            'تحلیل تکنیکال', 'مدیریت ریسک', 'الگوهای نموداری',
            'اندیکاتور', 'ایچیموکو', 'فیبوناچی'
        ]
        for tag_name in tags:
            slug = slugify(tag_name)
            if not Tag.objects.filter(slug=slug).exists():
                Tag.objects.create(
                    name=tag_name,
                    slug=slug
                )

    def create_articles(self):
        self.stdout.write('Creating articles...')
        users = User.objects.filter(is_staff=True)
        regular_users = list(User.objects.filter(is_staff=False))
        categories = Category.objects.all()
        tags = Tag.objects.all()
        
        article_titles = [
            'راهنمای کامل ترید بیت‌کوین برای مبتدیان',
            'اصول اولیه تحلیل تکنیکال در بازار کریپتو',
            '10 اشتباه رایج در معاملات ارزهای دیجیتال',
            'روانشناسی بازار: چگونه احساسات خود را کنترل کنیم',
            'استراتژی‌های مدیریت سرمایه در ترید',
            'آشنایی با الگوهای کندل استیک ژاپنی',
            'راهنمای جامع استفاده از فیبوناچی در تحلیل تکنیکال',
            'تحلیل فاندامنتال: چگونه پروژه‌های برتر را شناسایی کنیم',
            'آموزش کار با صرافی‌های ارز دیجیتال',
            'مفاهیم پایه بلاکچین و ارزهای دیجیتال'
        ]
        
        for title in article_titles:
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            
            # Keep trying with incremented counter until we find a unique slug
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            article = Article.objects.create(
                title=title,
                slug=slug,
                content='\n'.join(fake.paragraphs(15)),
                summary=fake.paragraph(),
                author=random.choice(users),
                category=random.choice(categories),
                status='published',
                published_at=timezone.now() - timedelta(days=random.randint(1, 100))
            )
            article.tags.set(random.sample(list(tags), min(6, len(tags))))
            
            # Add comments
            for _ in range(random.randint(3, 8)):
                comment = Comment.objects.create(
                    article=article,
                    author=random.choice(regular_users),
                    content=fake.paragraph(),
                    is_approved=True
                )
                
                # Add some replies
                if random.random() > 0.5:
                    Comment.objects.create(
                        article=article,
                        author=random.choice(users),
                        content=fake.paragraph(),
                        parent=comment,
                        is_approved=True
                    )
            
            # Add ratings
            # Randomly select users for rating without duplicates
            rating_users = random.sample(regular_users, min(len(regular_users), random.randint(5, 15)))
            for user in rating_users:
                Rating.objects.create(
                    article=article,
                    user=user,
                    value=random.randint(3, 5)  # بیشتر رتبه‌ها مثبت باشند
                )

    def create_media_categories(self):
        self.stdout.write('Creating media categories...')
        categories = [
            'تحلیل‌های روزانه',
            'آموزش‌های تکنیکال',
            'آموزش‌های فاندامنتال',
            'روانشناسی ترید',
            'لایو استریم',
            'مصاحبه با تریدرها',
            'اخبار و تحلیل بازار'
        ]
        for cat_name in categories:
            slug = slugify(cat_name)
            if not MediaCategory.objects.filter(slug=slug).exists():
                MediaCategory.objects.create(
                    name=cat_name,
                    slug=slug,
                    description=fake.paragraph()
                )

    def create_media_content(self):
        self.stdout.write('Creating media content...')
        users = User.objects.filter(is_staff=True)
        categories = MediaCategory.objects.all()
        tags = Tag.objects.all()
        
        # Create podcasts
        podcast_titles = [
            'تحلیل هفتگی بازار کریپتو',
            'بررسی روند بیت‌کوین',
            'مصاحبه با تریدرهای موفق',
            'آموزش استراتژی‌های معاملاتی',
            'اخبار مهم هفته در دنیای کریپتو'
        ]
        
        for i, title in enumerate(podcast_titles):
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            
            # Keep trying with incremented counter until we find a unique slug
            while Podcast.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            podcast = Podcast.objects.create(
                title=title,
                slug=slug,
                description=fake.paragraph(),
                category=random.choice(categories),
                author=random.choice(users),
                status='published',
                duration=timedelta(minutes=random.randint(30, 90)),
                episode_number=i+1,
                season_number=1
            )
            podcast.tags.set(random.sample(list(tags), min(4, len(tags))))
        
        # Create videos
        video_titles = [
            'آموزش تحلیل تکنیکال - قسمت 1',
            'آموزش تحلیل تکنیکال - قسمت 2',
            'معرفی اندیکاتورهای پرکاربرد',
            'آموزش الگوهای هارمونیک',
            'روانشناسی معاملات'
        ]
        
        for i, title in enumerate(video_titles):
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            
            # Keep trying with incremented counter until we find a unique slug
            while Video.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            video = Video.objects.create(
                title=title,
                slug=slug,
                description=fake.paragraph(),
                category=random.choice(categories),
                author=random.choice(users),
                status='published',
                video_type='youtube',
                video_url=f'https://youtube.com/watch?v={fake.uuid4()}',
                duration=timedelta(minutes=random.randint(20, 45)),
                is_premium=bool(i % 2)  # هر ویدیوی دوم پریمیوم باشد
            )
            video.tags.set(random.sample(list(tags), min(4, len(tags))))

    def create_courses(self):
        self.stdout.write('Creating courses...')
        instructors = User.objects.filter(is_staff=True)
        
        courses_data = [
            {
                'title': 'دوره جامع ترید ارزهای دیجیتال',
                'price': 4990000,
                'chapters': [
                    {
                        'title': 'مقدمات و آشنایی با بازار کریپتو',
                        'lessons': [
                            'معرفی بازار ارزهای دیجیتال',
                            'آشنایی با بیت‌کوین و بلاکچین',
                            'انواع ارزهای دیجیتال',
                            'کیف پول‌ها و امنیت',
                        ]
                    },
                    {
                        'title': 'تحلیل تکنیکال مقدماتی',
                        'lessons': [
                            'مفاهیم پایه تحلیل تکنیکال',
                            'انواع نمودارها',
                            'حمایت و مقاومت',
                            'الگوهای کندل استیک',
                            'خطوط روند'
                        ]
                    },
                    {
                        'title': 'تحلیل تکنیکال پیشرفته',
                        'lessons': [
                            'الگوهای هارمونیک',
                            'امواج الیوت',
                            'فیبوناچی پیشرفته',
                            'اندیکاتورها'
                        ]
                    },
                    {
                        'title': 'مدیریت سرمایه و ریسک',
                        'lessons': [
                            'اصول مدیریت سرمایه',
                            'محاسبه حجم معاملات',
                            'تعیین حد سود و ضرر',
                            'روش‌های مدیریت ریسک'
                        ]
                    }
                ]
            },
            {
                'title': 'دوره تحلیل تکنیکال پیشرفته',
                'price': 2990000,
                'chapters': [
                    {
                        'title': 'الگوهای پیشرفته نموداری',
                        'lessons': [
                            'الگوهای کلاسیک',
                            'الگوهای هارمونیک',
                            'الگوهای پیچیده'
                        ]
                    },
                    {
                        'title': 'استراتژی‌های معاملاتی',
                        'lessons': [
                            'ترید در روند',
                            'ترید در رنج',
                            'اسکالپینگ',
                            'سوینگ'
                        ]
                    }
                ]
            },
            {
                'title': 'دوره روانشناسی معاملات',
                'price': 1990000,
                'chapters': [
                    {
                        'title': 'مبانی روانشناسی بازار',
                        'lessons': [
                            'شناخت احساسات در معاملات',
                            'کنترل ترس و طمع',
                            'مدیریت استرس'
                        ]
                    },
                    {
                        'title': 'تکنیک‌های ذهنی',
                        'lessons': [
                            'ذهنیت برنده',
                            'نظم و انضباط در معاملات',
                            'ثبت و بررسی معاملات'
                        ]
                    }
                ]
            }
        ]
        
        for course_data in courses_data:
            base_slug = slugify(course_data['title'])
            slug = base_slug
            counter = 1
            
            # Keep trying with incremented counter until we find a unique slug
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            course = Course.objects.create(
                title=course_data['title'],
                slug=slug,
                description=fake.text(1000),
                instructor=random.choice(instructors),
                price=course_data['price'],
                is_free=False,
                # is_published=True
            )
            
            # Create chapters
            for chapter_idx, chapter_data in enumerate(course_data['chapters'], 1):
                chapter = Chapter.objects.create(
                    course=course,
                    title=chapter_data['title'],
                    description=fake.paragraph(),
                    order=chapter_idx
                )
                
                # Create lessons
                for lesson_idx, lesson_title in enumerate(chapter_data['lessons'], 1):
                    Lesson.objects.create(
                        chapter=chapter,
                        title=lesson_title,
                        content=fake.text(500),
                        video_url=f'https://example.com/videos/{fake.uuid4()}',
                        duration=random.randint(20, 60),
                        order=lesson_idx,
                        is_free_preview=lesson_idx == 1  # اولین درس هر فصل رایگان
                    )
            
            # Create discount
            if random.random() > 0.5:
                Discount.objects.create(
                    course=course,
                    code=f'TRADE{random.randint(1000, 9999)}',
                    percentage=random.choice([10, 15, 20, 25, 30]),
                    start_date=timezone.now() - timedelta(days=10),
                    end_date=timezone.now() + timedelta(days=20),
                    is_active=True,
                    max_uses=50,
                    current_uses=random.randint(0, 25)
                )
            
            # Create enrollments
            users = User.objects.filter(is_staff=False)
            for _ in range(random.randint(10, 30)):
                user = random.choice(users)
                if not Enrollment.objects.filter(user=user, course=course).exists():
                    Enrollment.objects.create(
                        user=user,
                        course=course,
                        price_paid=course.price,
                        enrolled_at=timezone.now() - timedelta(days=random.randint(1, 90))
                    ) 