from django.urls import path
from .views import OwnerDetailCafeListView

app_name = 'owners'

urlpatterns = [
    path('<int:owner_id>/cafes/', OwnerDetailCafeListView.as_view(), name='owner_detail_cafe_list'),
]
