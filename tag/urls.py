from django.urls import path
from .views import TagListView, CafeTagRatingView, CafeTagRatingDetailView

app_name = 'tags'

urlpatterns = [
    path("", TagListView.as_view),
    path("", CafeTagRatingView.as_view),
    path("<int:rating_id>/", CafeTagRatingDetailView.as_view),
]
