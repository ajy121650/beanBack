from django.urls import path
from .views import TableListView, TableDetailView

app_name = 'tables'

urlpatterns = [
    path("", TableListView.as_view(), name='list'),
    path("<int:table_id>/", TableDetailView.as_view(), name='detail'),
]