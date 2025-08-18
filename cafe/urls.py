from django.urls import path
from .views import CafeListView, CafeDetailView, CafeChatView

app_name = 'cafes'

urlpatterns = [
    path("", CafeListView.as_view()),
    path("<int:owner_id>/", CafeDetailView.as_view()),
    path("chat/", CafeChatView.as_view(), name='chat'),
]