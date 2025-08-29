from rest_framework import viewsets, permissions, serializers
from .models import Podcast, Episode
from .serializers import PodcastSerializer, EpisodeSerializer

class PodcastViewSet(viewsets.ModelViewSet):
    serializer_class = PodcastSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return podcasts owned by the logged-in user
        return Podcast.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EpisodeViewSet(viewsets.ModelViewSet):
    serializer_class = EpisodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only episodes that belong to the user's podcasts
        return Episode.objects.filter(podcast__user=self.request.user)

    def perform_create(self, serializer):
        podcast_id = self.request.data.get("podcast")
        if not podcast_id:
            raise serializers.ValidationError({"podcast": "This field is required."})
        podcast = Podcast.objects.filter(id=podcast_id, user=self.request.user).first()
        if not podcast:
            raise serializers.ValidationError({"podcast": "Invalid podcast id or you do not own this podcast."})
        serializer.save(podcast=podcast)
