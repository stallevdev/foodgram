"""Маршруты для API-приложения."""

from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet, TagViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
