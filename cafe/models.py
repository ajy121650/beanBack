from django.db import models
from tag.models import Tag
from owner.models import Owner

#카페 전체 정보 모델
class Cafe(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    average_rating = models.FloatField(default=0.0)
    photo_urls = models.JSONField(default=list, blank=True)
    embeddings = models.JSONField(default=list, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, through='CafeTagRating', related_name='cafes')
    keywords = models.ManyToManyField(Tag, blank=True, related_name="keyword")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.address})"
    
#카페 태그 별 별점 정보 모델
class CafeTagRating(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('cafe', 'tag')