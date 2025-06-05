import os
import django
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.utils.text import slugify
import random
import string
from course.models import Course, Comment

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trade.settings')
django.setup()

from django.contrib.auth import get_user_model
from course.models import Course, Chapter, Lesson, Discount, Comment
from blog.models import Category, Tag, Article

User = get_user_model()

def generate_unique_slug(title, model):
    """Generate a unique slug by adding random suffix if needed"""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while model.objects.filter(slug=slug).exists():
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        slug = f"{base_slug}-{random_suffix}"
        counter += 1
    
    return slug

def clear_existing_data():
    """Clear existing test data"""
    print("Clearing existing data...")
    # Delete test users
    User.objects.filter(phone_number__in=['09121111111', '09122222222', '09123333333']).delete()
    
    # Delete all courses and related data
    Course.objects.all().delete()
    
    # Delete all blog content
    Category.objects.all().delete()
    Tag.objects.all().delete()
    Article.objects.all().delete()
    print("Existing data cleared successfully!")

def create_test_instructors():
    instructors_data = [
        {
            'phone_number': '09121111111',
            'first_name': 'علی',
            'last_name': 'محمدی',
            'is_staff': True,
            'is_active': True,
            'is_phone_verified': True
        },
        {
            'phone_number': '09122222222',
            'first_name': 'سارا',
            'last_name': 'احمدی',
            'is_staff': True,
            'is_active': True,
            'is_phone_verified': True
        },
        {
            'phone_number': '09123333333',
            'first_name': 'محمد',
            'last_name': 'حسینی',
            'is_staff': True,
            'is_active': True,
            'is_phone_verified': True
        }
    ]
    
    instructors = []
    for instructor_data in instructors_data:
        instructor, created = User.objects.get_or_create(
            phone_number=instructor_data['phone_number'],
            defaults=instructor_data
        )
        if created:
            instructor.set_password('test12345')
            instructor.save()
        instructors.append(instructor)
    return instructors

def create_test_courses(instructors):
    # Create Courses
    courses_data = [
        {
            'title': 'مبانی تحلیل تکنیکال در بازارهای مالی',
            'description': '''در این دوره با اصول اولیه تحلیل تکنیکال، نمودارها، الگوهای قیمتی و اندیکاتورهای پرکاربرد آشنا خواهید شد.

مباحث دوره:
- آشنایی با انواع نمودارها و تایم‌فریم‌ها
- شناخت روندها و سطوح حمایت و مقاومت
- الگوهای کلاسیک قیمتی
- اندیکاتورهای پرکاربرد و نحوه استفاده از آنها
- استراتژی‌های معاملاتی بر اساس تحلیل تکنیکال''',
            'price': Decimal('1990000'),
            'is_published': True,
            'instructor': instructors[0]
        },
        {
            'title': 'آموزش جامع ترید در بازار کریپتوکارنسی',
            'description': '''آموزش کامل نحوه معامله در بازار ارزهای دیجیتال، استراتژی‌های معاملاتی و مدیریت ریسک

مباحث دوره:
- آشنایی با مفاهیم پایه ارزهای دیجیتال
- نحوه کار با صرافی‌های معتبر
- استراتژی‌های معاملاتی در بازار کریپتو
- مدیریت سرمایه و ریسک
- تحلیل فاندامنتال و تکنیکال در بازار کریپتو''',
            'price': Decimal('2490000'),
            'is_published': True,
            'instructor': instructors[1]
        },
        {
            'title': 'مدیریت سرمایه و روانشناسی معاملات',
            'description': '''اصول مدیریت سرمایه، کنترل ریسک و جنبه‌های روانشناختی معاملات در بازارهای مالی

مباحث دوره:
- اصول اولیه مدیریت سرمایه
- محاسبه حجم معاملات و ریسک هر معامله
- کنترل احساسات در معاملات
- روانشناسی بازار و رفتار معامله‌گران
- تکنیک‌های حفظ سلامت روان در معاملات''',
            'price': Decimal('1790000'),
            'is_published': True,
            'instructor': instructors[2]
        },
        {
            'title': 'آموزش فارکس از صفر تا صد',
            'description': '''آموزش کامل بازار فارکس، نحوه تحلیل، استراتژی‌های معاملاتی و کار با پلتفرم‌های معاملاتی

مباحث دوره:
- آشنایی با بازار فارکس و مفاهیم پایه
- کار با پلتفرم متاتریدر
- استراتژی‌های معاملاتی در فارکس
- مدیریت ریسک و سرمایه
- تحلیل تکنیکال و فاندامنتال در فارکس''',
            'price': Decimal('2990000'),
            'is_published': True,
            'instructor': instructors[0]
        },
    ]

    for course_data in courses_data:
        instructor = course_data.pop('instructor')
        # Generate unique slug before creating the course
        slug = generate_unique_slug(course_data['title'], Course)
        course = Course.objects.create(
            instructor=instructor,
            slug=slug,  # Set the slug explicitly
            **course_data
        )
        
        # Create Chapters for each course
        chapters_data = [
            {
                'title': 'مقدمات و آشنایی با مفاهیم پایه',
                'description': 'در این فصل با مفاهیم اولیه و پایه‌ای آشنا خواهید شد',
                'order': 1
            },
            {
                'title': 'تکنیک‌ها و استراتژی‌های اصلی',
                'description': 'آموزش تکنیک‌ها و استراتژی‌های کاربردی',
                'order': 2
            },
            {
                'title': 'پیشرفته و جمع‌بندی',
                'description': 'مباحث پیشرفته و جمع‌بندی دوره',
                'order': 3
            }
        ]
        
        for chapter_data in chapters_data:
            chapter = Chapter.objects.create(
                course=course,
                **chapter_data
            )
            
            # Create Lessons for each chapter
            for j in range(1, 4):
                Lesson.objects.create(
                    chapter=chapter,
                    title=f'درس {j}',
                    content=f'محتوای درس {j} از {chapter.title}',
                    duration=45,
                    order=j,
                    is_free_preview=j == 1  # First lesson is free preview
                )

        # Create a discount for each course
        Discount.objects.create(
            course=course,
            code=f'TRADE{course.id}',
            percentage=20,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            max_uses=100
        )

def create_test_blog_content(authors):
    # Create Categories
    categories_data = [
        'تحلیل تکنیکال',
        'ارزهای دیجیتال',
        'فارکس',
        'روانشناسی معاملات',
        'اخبار بازار',
        'آموزش مقدماتی',
        'استراتژی معاملاتی'
    ]
    
    categories = []
    for cat_name in categories_data:
        slug = generate_unique_slug(cat_name, Category)
        category, _ = Category.objects.get_or_create(
            name=cat_name,
            defaults={'slug': slug}
        )
        categories.append(category)

    # Create Tags
    tags_data = [
        'بیت‌کوین', 'اتریوم', 'تحلیل تکنیکال', 'مدیریت ریسک', 
        'روند بازار', 'استراتژی معاملاتی', 'NFT', 'DeFi',
        'متاورس', 'فارکس', 'تحلیل بنیادی', 'ارز دیجیتال'
    ]
    
    tags = []
    for tag_name in tags_data:
        slug = generate_unique_slug(tag_name, Tag)
        tag, _ = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': slug}
        )
        tags.append(tag)

    # Create Articles
    articles_data = [
        {
            'title': 'راهنمای کامل خرید و فروش بیت‌کوین',
            'content': '''در این مقاله به طور کامل نحوه خرید و فروش بیت‌کوین را آموزش خواهیم داد.

- انتخاب کیف پول مناسب
- نحوه خرید از صرافی‌های معتبر
- نکات امنیتی مهم
- استراتژی‌های خرید و فروش''',
            'category': categories[1],  # ارزهای دیجیتال
            'status': 'published',
            'author': authors[0]
        },
        {
            'title': 'اصول اولیه تحلیل تکنیکال برای تازه‌کاران',
            'content': '''آموزش گام به گام مفاهیم پایه تحلیل تکنیکال برای شروع معاملات.

- آشنایی با نمودارها
- خطوط روند
- حمایت و مقاومت
- الگوهای قیمتی ساده''',
            'category': categories[0],  # تحلیل تکنیکال
            'status': 'published',
            'author': authors[1]
        },
        {
            'title': '۵ اشتباه رایج در معاملات فارکس',
            'content': '''بررسی اشتباهات متداول معامله‌گران تازه‌کار در بازار فارکس.

- عدم مدیریت ریسک
- معامله با حجم بالا
- عدم استفاده از حد ضرر
- معامله بدون استراتژی
- تصمیم‌گیری احساسی''',
            'category': categories[2],  # فارکس
            'status': 'published',
            'author': authors[2]
        },
        {
            'title': 'چگونه استرس معاملات را کنترل کنیم؟',
            'content': '''راهکارهای عملی برای مدیریت استرس در معاملات و حفظ سلامت روان.

- تکنیک‌های تنفسی
- مدیریت احساسات
- برنامه‌ریزی معاملاتی
- اهمیت استراحت''',
            'category': categories[3],  # روانشناسی معاملات
            'status': 'published',
            'author': authors[0]
        },
        {
            'title': 'آینده DeFi و تاثیر آن بر بازار کریپتو',
            'content': '''بررسی روند توسعه فایننس غیرمتمرکز و تاثیر آن بر آینده ارزهای دیجیتال.

- مفهوم DeFi
- پروتکل‌های مهم
- فرصت‌های سرمایه‌گذاری
- ریسک‌ها و چالش‌ها''',
            'category': categories[1],  # ارزهای دیجیتال
            'status': 'published',
            'author': authors[1]
        }
    ]
    
    for article_data in articles_data:
        author = article_data.pop('author')
        # Generate unique slug for article
        slug = generate_unique_slug(article_data['title'], Article)
        article = Article.objects.create(
            author=author,
            slug=slug,
            **article_data
        )
        # Add random tags to each article
        article.tags.add(*tags[:3])


def create_test_comments(courses, users):
    print("Creating test comments for courses...")

    comments_data = [
        "این دوره عالی بود! خیلی چیزها یاد گرفتم.",
        "محتوای دوره بسیار کاربردی و مفید بود.",
        "استاد خیلی خوب توضیح می‌داد. ممنون از زحماتشون.",
        "کاش مثال‌های بیشتری در دوره گنجانده می‌شد.",
        "من این دوره رو به همه دوستانم پیشنهاد می‌کنم.",
        "بعضی قسمت‌ها نیاز به توضیح بیشتری داشت.",
        "خیلی خوب بود ولی کاش طولانی‌تر بود.",
        "سوال‌هام به خوبی پاسخ داده شد. ممنون از پشتیبانی خوبتون.",
        "این دوره دید من رو نسبت به این موضوع کاملاً تغییر داد.",
        "منتظر دوره‌های پیشرفته‌تر در این زمینه هستم."
    ]

    reply_data = [
        "ممنون از نظر مثبت شما!",
        "خوشحالیم که دوره برایتان مفید بوده است.",
        "حتماً پیشنهاد شما رو در نظر می‌گیریم.",
        "در دوره‌های بعدی سعی می‌کنیم این مورد رو بهبود بدیم.",
        "از حمایت شما سپاسگزاریم."
    ]

    for course in courses:
        # ایجاد 3 تا 7 کامنت اصلی برای هر دوره
        for _ in range(random.randint(3, 7)):
            comment = Comment.objects.create(
                course=course,
                user=random.choice(users),
                content=random.choice(comments_data),
                is_approved=random.choice([True, False])
            )

            # احتمال 50٪ برای ایجاد پاسخ به این کامنت
            if random.choice([True, False]):
                Comment.objects.create(
                    course=course,
                    user=course.instructor,  # پاسخ از طرف مدرس
                    content=random.choice(reply_data),
                    parent=comment,
                    is_approved=True
                )

    print(f"Created test comments for {len(courses)} courses.")

courses = Course.objects.all()
users = User.objects.all()

create_test_comments(courses, users)