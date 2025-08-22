from django.db import models
from cafe.models import Cafe

# 카페 도면 모델
class FloorPlan(models.Model):
    width = models.FloatField(default=0)
    height = models.FloatField(default=0.0)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='floor_plans')

    def __str__(self):
        return f"FloorPlan for {self.cafe.name} ({self.width}x{self.height})"