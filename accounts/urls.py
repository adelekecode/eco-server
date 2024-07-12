from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()



urlpatterns = [
    path('auth/', include(router.urls)),
    # path('auth/', include('social_auth.urls')),
    # path('auth/admin/', views.AdminListCreateView().as_view()),
    path('auth/', views.user_auth, name="login_view"),
    path("auth/logout/", views.logout_view, name="logout_view"),
    path('auth/verify/', views.otp_verification),


]
