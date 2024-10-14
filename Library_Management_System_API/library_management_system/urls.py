"""
URL configuration for library_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer

schema_view = get_schema_view(
    title = 'Library Management API',
    description = 'A library management api that allows users to easily access available books in the library also be able to checkout the users favorite book or desired book and return it after 14 days after the 14 days you get fined and any additional day after',
    version = '1.0.0',
    renderer_classes = [JSONOpenAPIRenderer]

)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library_api.urls')),
    path('', schema_view, name='api-schema'),
]
