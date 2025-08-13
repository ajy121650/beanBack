from django.db import models
from floorplan.models import FloorPlan
from django.utils import timezone
# Create your models here.

class Chair(models.Model):
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    x_position = models.FloatField(default=0.0)
    y_position = models.FloatField(default=0.0)
    socket = models.BooleanField(default=False)
    window = models.BooleanField(default=False)
    occupied = models.BooleanField(default=False)
    floor_plan = models.ForeignKey(FloorPlan, on_delete=models.CASCADE, related_name='chairs')
    entry_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Chair at ({self.x_position}, {self.y_position}) in {self.floor_plan.cafe.name} ({self.width}x{self.height})"