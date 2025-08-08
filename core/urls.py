from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from core.admin_views import admin_stats_api

schema_view = get_schema_view(
   openapi.Info(
      title="GradFund API",
      default_version='v1',
      description="GradFund API documentation",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
   path('admin/', admin.site.urls),
   path('admin/api/stats/', admin_stats_api, name='admin-stats-api'),
   path('api/v1/', include('apps.academic.urls')),
   path('api/v1/', include('apps.services.urls')),
   path('api/v1/auth/', include('apps.authentication.urls')),
   path('api/v1/chat/', include('apps.chat.urls')),
   path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
