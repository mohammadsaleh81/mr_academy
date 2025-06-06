"""
URL configuration for trade project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from payment.views import VerifyView, CreatePayment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('content/', include('blog.urls')),
    path('crs/', include('course.urls')),
    path('user/', include('user.urls')),
    path('pay/', include('payment.urls')),
    path('wallet/', include('wallet.urls', namespace='wallet')),
    path('order/', include('order.urls', namespace='order')),


                  # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI - you can use either Swagger or Redoc or both
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # ... other url patterns ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)