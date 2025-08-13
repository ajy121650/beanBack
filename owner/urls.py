from django.urls import path
from .views import SignUpView, SignInView, OwnerDetailCafeListView

app_name = 'owners'

urlpatterns = [
    path("signup/", SignUpView.as_view()),
    path("signin/", SignInView.as_view()),
    path('<int:owner_id>/cafes/', OwnerDetailCafeListView.as_view(), name='owner_detail_cafe_list'),
]

