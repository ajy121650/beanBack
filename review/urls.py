from django.urls import path
from .views import ReviewListView, ReviewDetailView

app_name = 'reviews'

urlpatterns = [
    path("", ReviewListView.as_view),
    path('<int:cafe_id>/', ReviewDetailView.as_view()),
]