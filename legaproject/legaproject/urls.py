"""
URL configuration for legaproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('cadastro/', views.cadastro_page, name='cadastro_page'),
    path('sobre/', views.sobre_page, name='sobre_page'),
    path('login/', views.login_page, name='login_page'),
    path('perfil/', views.perfil_page, name='perfil_page'),
    path('tarefas/', views.tarefas_page, name='tarefas_page'),
    path('trilhas/', views.roadmaps_page, name='roadmaps_page'),
    path('calendario/', views.calendario_page, name='calendario_page'),
    path('gerador-roadmap/', views.roadmap_page, name='roadmap_page'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
