from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from character_viewer.views import custom_logout
from character_viewer.views.health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('character_viewer.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', custom_logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('health/', health_check, name='health_check'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production on Render, serve media files as well (though not optimal for performance)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)