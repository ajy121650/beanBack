from django.urls import path
from .views import ReviewCrawlingView, ReviewListView, ReviewDetailView

app_name = 'reviews'

urlpatterns = [
    path("crawl_reviews/", ReviewCrawlingView.as_view(), name="crawl_reviews"),
    path("", ReviewListView.as_view),
    path('<int:cafe_id>/', ReviewDetailView.as_view()),
]