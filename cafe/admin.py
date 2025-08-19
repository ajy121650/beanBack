from django.contrib import admin

# Register your models here.
from .models import Cafe, CafeTagRating

admin.site.register(Cafe)
admin.site.register(CafeTagRating)