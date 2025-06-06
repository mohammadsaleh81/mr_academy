from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'blog'

urlpatterns = [

    # Article URLs
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<int:pk>/comments/', views.ArticleCommentView.as_view(), name='article-comments'),

    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Video URLs
    path('videos/', views.VideoListView.as_view(), name='video-list'),
    path('videos/<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    path('videos/<int:pk>/comments/', views.VideoCommentView.as_view(), name='video-comments'),

    # Podcast URLs
    path('podcasts/', views.PodcastListView.as_view(), name='podcast-list'),
    path('podcasts/<int:pk>/', views.PodcastDetailView.as_view(), name='podcast-detail'),
    path('podcasts/<int:pk>/comments/', views.PodcastCommentView.as_view(), name='podcast-comments'),

    # Comment URLs (for articles)
    path('comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),

    # Media Comment URLs (for all media types)
    path('media-comments/', views.MediaCommentView.as_view(), name='media-comments'),
    path('media-comments/list/', views.MediaCommentListCreateView.as_view(), name='media-comment-list'),
    path('media-comments/<int:pk>/', views.MediaCommentDetailView.as_view(), name='media-comment-detail'),

    # Like URLs
    path('likes/', views.ArticleLikeListCreateView.as_view(), name='like-list'),
    path('likes/<int:pk>/', views.ArticleLikeDetailView.as_view(), name='like-detail'),

    # Bookmark URLs
    path('bookmarks/', views.ArticleBookmarkListCreateView.as_view(), name='bookmark-list'),
    path('bookmarks/<int:pk>/', views.ArticleBookmarkDetailView.as_view(), name='bookmark-detail'),
]