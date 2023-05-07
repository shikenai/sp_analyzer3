"""
URL configuration for sp_analyzer3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from myapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/register_brands.json", views.register_brands),
    path("api/register_trades.json", views.register_trades),
    path("api/get_new_trades.json", views.get_new_trades),
    path("api/analyze.json", views.analyze),
    path("api/show.json", views.show),
    path("api/reg_judge", views.reg_judge),
    path("api/get_states.json", views.get_states),
    path("", views.home),
]
