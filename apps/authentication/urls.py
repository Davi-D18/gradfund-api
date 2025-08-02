from django.urls import path
from apps.authentication.controllers import RegisterView, CustomTokenObtainPairView, TokenRefreshView, DeleteView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
    path('delete/<int:user_id>/', DeleteView.as_view(), name='delete'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]