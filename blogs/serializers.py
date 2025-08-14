from rest_framework import serializers
from .models import Post, Tag, BlogImage


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['id', 'image', 'caption']


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )
    images = BlogImageSerializer(many=True, read_only=True)

    # For uploading images on create/update, expect a separate images upload endpoint (recommended for large files)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'tags', 'tag_ids', 'images', 'status', 'scheduled_publish',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        post = Post.objects.create(**validated_data)
        post.tags.set(tag_ids)
        return post

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        return instance


class BlogImageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used for image uploads with post ID.
    """
    class Meta:
        model = BlogImage
        fields = ['id', 'post', 'image', 'caption']
