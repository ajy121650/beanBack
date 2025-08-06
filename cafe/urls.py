from django.urls import path
from .views import CafeUploadView, CafeListView, CafeDetailView, CafeImageUpdateView, CafeChatView

app_name = 'cafes'

urlpatterns = [
    path("upload-cafes/", CafeUploadView.as_view(), name='upload_cafes'),
    path("update-images/", CafeImageUpdateView.as_view(), name='update_images'),
    path("", CafeListView.as_view()),
    path("<int:cafe_id>/", CafeDetailView.as_view()),
    path("chat/", CafeChatView.as_view(), name='chat'),
]