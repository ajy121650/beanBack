from django.db import models
from floorplan.models import FloorPlan
# Create your models here.

class Table(models.Model):
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    x_position = models.FloatField(default=0.0)
    y_position = models.FloatField(default=0.0)
    shape = models.CharField(max_length=50, default='rectangle')
    seat_number = models.CharField(max_length=50, default='4인석')
    floor_plan = models.ForeignKey(FloorPlan, on_delete=models.CASCADE, related_name='tables')

    def __str__(self):
        return f"Table at ({self.x_position}, {self.y_position}) in {self.floor_plan.cafe.name} ({self.width}x{self.height})"  
