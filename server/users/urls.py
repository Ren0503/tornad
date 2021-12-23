from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


app_name = 'users-api'

urlpatterns = [
    path('', views.users, name='users'),
    path('recommended/', views.users_recommended, name="users-recommended"),

    path('profile/', views.profile, name='profile'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.MyTokenObtainPairView.as_view(), name='login'),
    path('following/', views.following, name='following'),
    path('refresh_token/', TokenRefreshView.as_view(), name='refresh_token'),

    path('profile_update/', views.UserProfileUpdate.as_view(), name="profile_update"), 
    path('profile_update/photo/', views.ProfilePictureUpdate.as_view(), name="profile_update_photo"), 
    path('<str:username>/follow/', views.follow_user, name="follow-user"),
    path('delete-profile/', views.delete_user, name="delete-user"),
    path('profile_update/delete/', views.ProfilePictureDelete, name="profile_delete_photo"), 
    path('<str:username>/', views.user, name="user"),
    path('<str:username>/writes/', views.user_writes, name="user-mumbles"),
]