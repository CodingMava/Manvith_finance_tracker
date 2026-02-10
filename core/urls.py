from django.urls import path, include
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path('accounts/', include('allauth.urls')),
    path('tracker/', include('apps.tracker.urls')),
]
