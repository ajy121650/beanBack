from django.db import models
from django.contrib.auth.models import User

class Owner(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"id={self.id}, user_id={self.owner.id}"