from django.db import models

# Create your models here.
class Cafe(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    average_rating = models.FloatField(default=0.0)
    photo_urls = models.JSONField(default=list, blank=True)  # list
    embeddings = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.address})"