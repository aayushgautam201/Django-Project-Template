from rest_framework import viewsets, permissions
from .models import Post, Tag, BlogImage
from .serializers import PostSerializer, TagSerializer, BlogImageSerializer, BlogImageCreateSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only post authors can modify/delete posts.
    Others can read.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related('author').prefetch_related('tags', 'images')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BlogImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet dedicated to BlogImage for efficient management of images.
    Uses different serializers for list/retrieve and create/update.
    """

    queryset = BlogImage.objects.select_related('post').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BlogImageCreateSerializer
        return BlogImageSerializer
