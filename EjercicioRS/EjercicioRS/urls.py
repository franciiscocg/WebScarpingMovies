from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [   
    path('admin/',admin.site.urls),
    path('mostrar_peliculas/', views.mostrar_peliculas, name='mostrar_peliculas'),
    path('cargar_index_y_BD/', views.cargar_index_y_BD, name='cargar_index_y_BD'),
    path('crear_index/', views.crear_index, name='crear_index'),
    ]
