#!/usr/bin/env python
"""
Simple test script for bookmark APIs
Run with: python test_bookmarks.py
"""

import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trade.settings')
django.setup()

from blog.models import Article, ArticleBookmark
from user.models import User

def test_bookmark_api():
    """Test bookmark API endpoints"""
    
    # API base URL
    BASE_URL = "http://91.99.49.130:8000"
    
    print("🧪 Testing Bookmark API...")
    
    # Test 1: Check if we have articles
    print("\n1. Checking articles...")
    articles = Article.objects.filter(status='published')[:5]
    print(f"   Found {articles.count()} published articles")
    
    if articles.count() == 0:
        print("   ❌ No articles found. Creating a test article...")
        # Create a test user if needed
        user, created = User.objects.get_or_create(
            phone_number='09123456789',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_phone_verified': True
            }
        )
        
        # Create a test article
        article = Article.objects.create(
            title='Test Article for Bookmarks',
            slug='test-article-bookmarks',
            content='This is a test article for bookmark functionality.',
            summary='Test article summary',
            author=user,
            status='published'
        )
        print(f"   ✅ Created test article: {article.title}")
        articles = [article]
    
    # Test 2: Check bookmark endpoints
    print("\n2. Testing bookmark endpoints...")
    
    # Test GET /content/bookmarks/ (without auth - should fail)
    print("   Testing GET /content/bookmarks/ without auth...")
    response = requests.get(f"{BASE_URL}/content/bookmarks/")
    print(f"   Status: {response.status_code} (Expected: 401 or 403)")
    
    # Test GET /content/articles/
    print("   Testing GET /content/articles/...")
    response = requests.get(f"{BASE_URL}/content/articles/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found {len(data)} articles in API response")
        if data:
            print(f"   First article: {data[0].get('title', 'No title')}")
    else:
        print(f"   ❌ Failed to get articles: {response.text}")
    
    # Test 3: Check database bookmarks
    print("\n3. Checking database bookmarks...")
    bookmarks = ArticleBookmark.objects.all()
    print(f"   Found {bookmarks.count()} bookmarks in database")
    
    if bookmarks.exists():
        for bookmark in bookmarks[:3]:
            print(f"   - User: {bookmark.user.phone_number}, Article: {bookmark.article.title}")
    
    print("\n✅ Bookmark API test completed!")
    print("\n📋 Summary:")
    print(f"   - Articles in DB: {Article.objects.filter(status='published').count()}")
    print(f"   - Bookmarks in DB: {ArticleBookmark.objects.count()}")
    print(f"   - Users in DB: {User.objects.count()}")
    
    print("\n🔗 API Endpoints:")
    print(f"   - Articles: {BASE_URL}/content/articles/")
    print(f"   - Bookmarks: {BASE_URL}/content/bookmarks/")
    print(f"   - Article Detail: {BASE_URL}/content/articles/{{id}}/")

if __name__ == "__main__":
    test_bookmark_api() 