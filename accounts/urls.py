from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.CustomUserViewSet, basename="user")




urlpatterns = [
    # path('auth/', include(router.urls)),
    # path('auth/', include('djoser.urls.jwt')),
    # path('auth/admin/', views.AdminListCreateView().as_view()),
    path('auth/token/', views.user_auth, name="login_view"),
    path("auth/logout/", views.logout_view, name="logout_view"),
    path('auth/verify/', views.otp_verification),
    path('teams/create/', views.teams_view),
    path('teams/join/', views.join_team),
    path('teams/list/', views.user_teams),
    path('teams/<uuid:pk>/leave/', views.leave_team),
    path('teams/<uuid:pk>/delete/', views.delete_team),
    path('scan/upload/', views.ApproximateImage.as_view()),
    path('scan/confirm-bin/', views.ConfirmBinView.as_view()),
    path('scan/list/', views.ScansView.as_view()),

]
