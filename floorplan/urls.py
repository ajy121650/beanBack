from django.urls import path
from .views import FloorPlanListView, FloorPlanDetailView, FloorPlanOwnerView ,FloorPlanDetectionView, FloorPlanCafeView

app_name = 'floorplans'

urlpatterns = [
    path("", FloorPlanListView.as_view(), name='list'),
    path("<int:floorplan_id>/", FloorPlanDetailView.as_view(), name='detail'),
    path("by-owner/<int:owner_id>/", FloorPlanOwnerView.as_view(), name='by-owner'),
    path("by-cafe/<int:cafe_id>/", FloorPlanCafeView.as_view(), name='by-cafe'),
    path("detection/", FloorPlanDetectionView.as_view(), name='detection'),
]