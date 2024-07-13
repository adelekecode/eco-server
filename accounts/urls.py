from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.CustomUserViewSet, basename="user")




urlpatterns = [
    path('auth/', include(router.urls)),
    # path('auth/', include('djoser.urls.jwt')),
    # path('auth/admin/', views.AdminListCreateView().as_view()),
    path('auth/token/', views.user_auth, name="login_view"),
    path("auth/logout/", views.logout_view, name="logout_view"),
    path('auth/verify/', views.otp_verification),
    path('teams/', views.teams_view),
    path('teams/user/join/', views.join_team),
    path('teams/users/', views.user_teams),


]
