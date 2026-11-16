from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('accounts:login')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)