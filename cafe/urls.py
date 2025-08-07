from django.urls import path
from .views import CafeUploadView, CafeListView, CafeDetailView, CafeImageUpdateView, CafeChatView

app_name = 'cafes'

urlpatterns = [
    path("upload_cafes/", CafeUploadView.as_view(), name='upload_cafes'),
    path("update_images/", CafeImageUpdateView.as_view(), name='update_images'),
    path("", CafeListView.as_view()),
    path("<int:owner_id>/", CafeDetailView.as_view()),
    path("chat/", CafeChatView.as_view(), name='chat'),
]