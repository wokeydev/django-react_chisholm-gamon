from rest_framework import serializers
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model


class AuthorSerializer(serializers.ModelSerializer):
    author_blog_slug = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'id', 'username', 'author_blog_slug')

    def get_author_blog_slug(self, obj):
        return reverse('blog:author', kwargs={'author': obj.username})
