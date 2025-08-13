"""
URL configuration for bean project.

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

# swagger imports
# import는 맨 위에서~
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# swagger settings
schema_view = get_schema_view(
    openapi.Info(
        title="Bean API",
        default_version='v1',
        description="Test description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cafes/', include('cafe.urls')), #cafe 폴더의 urls.py 파일로 가서 이후 url을 찾아라
    path('api/reviews/', include('review.urls')),
    path('api/tags/', include('tag.urls')),
    path('api/floorplans/', include('floorplan.urls')),
    path('api/chairs/', include('chair.urls')),    
    path('api/tables/', include('table.urls')), 
    path('api/owners/', include('owner.urls')),   

    # swagger path
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
