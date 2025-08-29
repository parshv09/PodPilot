from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PodcastViewSet, EpisodeViewSet

router = DefaultRouter()
router.register(r'podcasts', PodcastViewSet, basename="podcast")
router.register(r'episodes', EpisodeViewSet, basename="episode")

urlpatterns = [
    path('', include(router.urls)),
]
