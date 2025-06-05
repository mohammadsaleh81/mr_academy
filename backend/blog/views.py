from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Article, Video, Podcast, Comment, ArticleLike, ArticleBookmark, Category
from .serializers import (
    ArticleSerializer, VideoSerializer, PodcastSerializer,
    CommentSerializer, ArticleLikeSerializer, ArticleBookmarkSerializer, CategorySerializer
)
from rest_framework.decorators import action

# Create your views here.

@extend_schema_view(
    get=extend_schema(
        summary="List all articles",
        description="Returns a list of all published articles.",
    ),
)
class ArticleListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        articles = Article.objects.filter(status='published')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve an article",
        description="Get detailed information about a specific article.",
    ),
)
class ArticleDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk, status='published')
        serializer = ArticleSerializer(article)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Get article comments",
        description="Returns a list of comments for a specific article.",
    ),
    post=extend_schema(
        summary="Add a comment",
        description="Add a new comment to an article. Must be authenticated.",
    ),
)
class ArticleCommentView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        comments = Comment.objects.filter(article=article, parent=None)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        serializer = CommentSerializer(data={**request.data, 'article': article.id})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="List all categories",
        description="Returns a list of all categories.",
    ),
)
class CategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a category",
        description="Get detailed information about a specific category.",
    ),
)
class CategoryDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="List all videos",
        description="Returns a list of all published videos.",
    ),
)
class VideoListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        videos = Video.objects.filter(status='published')
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a video",
        description="Get detailed information about a specific video.",
    ),
)
class VideoDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk, status='published')
        serializer = VideoSerializer(video)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="List all podcasts",
        description="Returns a list of all published podcasts.",
    ),
)
class PodcastListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        podcasts = Podcast.objects.filter(status='published')
        serializer = PodcastSerializer(podcasts, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a podcast",
        description="Get detailed information about a specific podcast.",
    ),
)
class PodcastDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        podcast = get_object_or_404(Podcast, pk=pk, status='published')
        serializer = PodcastSerializer(podcast)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="List article comments",
        description="Returns a list of comments for a specific article.",
    ),
    post=extend_schema(
        summary="Create a comment",
        description="Create a new comment for an article. Must be authenticated.",
    ),
)
class CommentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        article_id = request.query_params.get('article')
        comments = Comment.objects.filter(parent=None)
        if article_id:
            comments = comments.filter(article_id=article_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve a comment",
        description="Get detailed information about a specific comment.",
    ),
    put=extend_schema(
        summary="Update a comment",
        description="Update a comment. Only the owner can update.",
    ),
    delete=extend_schema(
        summary="Delete a comment",
        description="Delete a comment. Only the owner can delete.",
    ),
)
class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Comment, pk=pk)

    def get(self, request, pk):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary="List likes",
        description="Returns a list of all likes for the current user.",
    ),
    post=extend_schema(
        summary="Create a like",
        description="Like an article. Must be authenticated.",
    ),
)
class ArticleLikeListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        likes = ArticleLike.objects.filter(user=request.user)
        serializer = ArticleLikeSerializer(likes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleLikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    delete=extend_schema(
        summary="Remove a like",
        description="Remove a like from an article. Only the owner can remove.",
    ),
)
class ArticleLikeDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        like = get_object_or_404(ArticleLike, pk=pk, user=request.user)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        summary="List bookmarks",
        description="Returns a list of all bookmarks for the current user.",
    ),
    post=extend_schema(
        summary="Create a bookmark",
        description="Bookmark an article. Must be authenticated.",
    ),
)
class ArticleBookmarkListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookmarks = ArticleBookmark.objects.filter(user=request.user)
        serializer = ArticleBookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleBookmarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    delete=extend_schema(
        summary="Remove a bookmark",
        description="Remove a bookmark from an article. Only the owner can remove.",
    ),
)
class ArticleBookmarkDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        bookmark = get_object_or_404(ArticleBookmark, pk=pk, user=request.user)
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user