from django.urls import path
from .views import SignUpView, SignInView, TokenRefreshView, SignOutView,UserInfoView, OwnerDetailCafeListView

app_name = 'owners'

urlpatterns = [
    path("signup/", SignUpView.as_view()),
    path("signin/", SignInView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("signout/", SignOutView.as_view()),  # Assuming you want to use the same view for signout
    path("info/", UserInfoView.as_view()),
    path('<int:owner_id>/cafes/', OwnerDetailCafeListView.as_view(), name='owner_detail_cafe_list'),
]

