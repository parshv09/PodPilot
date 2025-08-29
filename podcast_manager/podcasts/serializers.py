from rest_framework import serializers
from .models import Podcast, Episode

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = [
            "id",
            "title",
            "description",
            "status",
            "scheduled_date",
            "created_at",
            "podcast",
        ]
        read_only_fields = ["id", "created_at", "podcast"]

    def validate(self, data):
        # Determine new or existing values (supports partial updates)
        status = data.get("status", getattr(self.instance, "status", None))
        scheduled_date = data.get("scheduled_date", getattr(self.instance, "scheduled_date", None))

        if status == "scheduled" and not scheduled_date:
            raise serializers.ValidationError({"scheduled_date": 'Scheduled date is required when status is "scheduled".'})
        if status != "scheduled" and scheduled_date:
            raise serializers.ValidationError({"scheduled_date": 'Scheduled date can only be set when status is "scheduled".'})
        return data


class PodcastSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Podcast
        fields = [
            "id",
            "title",
            "description",
            "status",
            "scheduled_date",
            "created_at",
            "episodes",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        # status and scheduled_date validation
        status = data.get("status", getattr(self.instance, "status", None))
        scheduled_date = data.get("scheduled_date", getattr(self.instance, "scheduled_date", None))

        if status == "scheduled" and not scheduled_date:
            raise serializers.ValidationError({"scheduled_date": 'Scheduled date is required when podcast status is "scheduled".'})
        if status != "scheduled" and scheduled_date:
            raise serializers.ValidationError({"scheduled_date": 'Scheduled date can only be set when podcast status is "scheduled".'})
        return data
