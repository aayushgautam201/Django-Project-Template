from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, TagViewSet, BlogImageViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('tags', TagViewSet, basename='tag')
router.register('images', BlogImageViewSet, basename='image')

urlpatterns = []
urlpatterns += router.urls
