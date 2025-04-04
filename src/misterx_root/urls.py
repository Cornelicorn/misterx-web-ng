"""
URL configuration for misterx_root project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from .forms import LoginForm
from .views import login_or_redirect, serve_protected_media

urlpatterns = [
    path("", include("social_django.urls", namespace="social")),
    path("", login_or_redirect),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("", include("misterx.urls")),
] + debug_toolbar_urls() + static(settings.MEDIA_URL, view=serve_protected_media, document_root=settings.MEDIA_ROOT)
