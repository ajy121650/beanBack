from django.urls import path
from .views import FloorPlanListView, FloorPlanDetailView, FloorPlanOwnerView ,FloorPlanDetectionView

app_name = 'floorplans'

urlpatterns = [
    path("", FloorPlanListView.as_view(), name='list'),
    path("<int:floorplan_id>/", FloorPlanDetailView.as_view(), name='detail'),
    path("by-owner/<int:owner_id>/", FloorPlanOwnerView.as_view(), name='owner'),
    path("detection/", FloorPlanDetectionView.as_view(), name='detection'),
]