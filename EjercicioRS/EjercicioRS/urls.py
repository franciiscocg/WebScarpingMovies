from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [   
    path('admin/',admin.site.urls),
    path('mostrar_peliculas/', views.mostrar_peliculas, name='mostrar_peliculas'),
    
    ]
