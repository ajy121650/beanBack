from django.urls import path
from .views import ChairListView, ChairDetailView

app_name = 'chairs'

urlpatterns = [
    path("", ChairListView.as_view(), name='list'),
    path("<int:chair_id>/", ChairDetailView.as_view(), name='detail'),
]