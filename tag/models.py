from django.db import models

# 태그 모델
class Tag(models.Model):
    content = models.TextField()