from django.db import models
from django.conf import settings

class Podcast(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("published", "Published"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="podcasts"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)  # New field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    scheduled_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # New field
    is_featured = models.BooleanField(default=False)  # New field to highlight popular podcasts

    def __str__(self):
        return self.title



class Episode(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("published", "Published"),
    ]

    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE,
        related_name="episodes"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.DurationField(null=True, blank=True)  # New field for length of episode
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    scheduled_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # New field
    audio_file = models.FileField(upload_to='episodes/', null=True, blank=True)  # Placeholder for future use

    def __str__(self):
        return f"{self.title} ({self.status})"

