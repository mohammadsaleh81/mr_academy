from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Article, Video, Podcast, Category, MediaCategory, Comment, MediaComment

User = get_user_model()

class CommentAPITestCase(APITestCase):
    def setUp(self):
        # ایجاد کاربران تست
        self.user = User.objects.create_user(
            phone_number='09123456789',
            password='testpass',
            first_name='تست',
            last_name='کاربر'
        )
        self.admin_user = User.objects.create_user(
            phone_number='09123456788',
            password='adminpass',
            first_name='ادمین',
            last_name='تست',
            is_staff=True
        )
        
        # ایجاد دسته‌بندی‌ها
        self.category = Category.objects.create(
            name='تست دسته‌بندی',
            slug='test-category'
        )
        self.media_category = MediaCategory.objects.create(
            name='تست رسانه',
            slug='test-media'
        )
        
        # ایجاد محتوا
        self.article = Article.objects.create(
            title='مقاله تست',
            slug='test-article',
            content='محتوای تست مقاله',
            author=self.admin_user,
            category=self.category,
            status='published'
        )
        
        self.video = Video.objects.create(
            title='ویدیو تست',
            slug='test-video',
            description='توضیحات ویدیو تست',
            author=self.admin_user,
            category=self.media_category,
            status='published',
            video_type='youtube',
            video_url='https://youtube.com/watch?v=test'
        )

    def test_article_comment_list(self):
        """تست دریافت لیست کامنت‌های مقاله"""
        # ایجاد کامنت
        Comment.objects.create(
            article=self.article,
            author=self.user,
            content='کامنت تست',
            is_approved=True
        )
        
        url = f'/api/blog/articles/{self.article.id}/comments/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'کامنت تست')

    def test_article_comment_create(self):
        """تست ایجاد کامنت برای مقاله"""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/blog/articles/{self.article.id}/comments/'
        data = {'content': 'کامنت جدید'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, 'کامنت جدید')

    def test_video_comment_list(self):
        """تست دریافت لیست کامنت‌های ویدیو"""
        # ایجاد کامنت رسانه
        content_type = ContentType.objects.get_for_model(Video)
        MediaComment.objects.create(
            content_type=content_type,
            object_id=self.video.id,
            author=self.user,
            content='کامنت ویدیو تست',
            is_approved=True
        )
        
        url = f'/api/blog/videos/{self.video.id}/comments/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'کامنت ویدیو تست')

    def test_video_comment_create(self):
        """تست ایجاد کامنت برای ویدیو"""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/blog/videos/{self.video.id}/comments/'
        data = {'content': 'کامنت ویدیو جدید'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MediaComment.objects.count(), 1)
        self.assertEqual(MediaComment.objects.first().content, 'کامنت ویدیو جدید')

    def test_media_comment_generic_api(self):
        """تست API عمومی کامنت رسانه"""
        self.client.force_authenticate(user=self.user)
        
        # تست ایجاد کامنت از طریق API عمومی
        url = '/api/blog/media-comments/'
        data = {
            'content_type': 'video',
            'object_id': self.video.id,
            'content': 'کامنت از API عمومی'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MediaComment.objects.count(), 1)

    def test_comment_reply(self):
        """تست پاسخ به کامنت"""
        # ایجاد کامنت اصلی
        parent_comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='کامنت اصلی',
            is_approved=True
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/blog/articles/{self.article.id}/comments/'
        data = {
            'content': 'پاسخ به کامنت',
            'parent': parent_comment.id
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        
        reply = Comment.objects.filter(parent=parent_comment).first()
        self.assertEqual(reply.content, 'پاسخ به کامنت')

    def test_comment_unauthorized(self):
        """تست ایجاد کامنت بدون احراز هویت"""
        url = f'/api/blog/articles/{self.article.id}/comments/'
        data = {'content': 'کامنت غیرمجاز'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_edit_permission(self):
        """تست ویرایش کامنت (فقط صاحب کامنت)"""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='کامنت اولیه'
        )
        
        # تست ویرایش توسط صاحب کامنت
        self.client.force_authenticate(user=self.user)
        url = f'/api/blog/comments/{comment.id}/'
        data = {'content': 'کامنت ویرایش شده'}
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # تست ویرایش توسط کاربر دیگر
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CommentModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            password='testpass',
            first_name='تست',
            last_name='کاربر'
        )
        
        self.category = Category.objects.create(
            name='تست دسته‌بندی',
            slug='test-category'
        )
        
        self.article = Article.objects.create(
            title='مقاله تست',
            slug='test-article',
            content='محتوای تست',
            author=self.user,
            category=self.category,
            status='published'
        )

    def test_comment_str(self):
        """تست نمایش رشته‌ای کامنت"""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='کامنت تست'
        )
        
        expected_str = f'نظر {self.user} در {self.article}'
        self.assertEqual(str(comment), expected_str)

    def test_comment_hierarchy(self):
        """تست سلسله مراتب کامنت‌ها"""
        parent_comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='کامنت اصلی'
        )
        
        reply_comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='پاسخ',
            parent=parent_comment
        )
        
        self.assertEqual(reply_comment.parent, parent_comment)
        self.assertIn(reply_comment, parent_comment.replies.all())
