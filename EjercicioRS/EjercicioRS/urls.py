from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [   
    path('admin/',admin.site.urls),
    path('mostrar_peliculas/', views.mostrar_peliculas, name='mostrar_peliculas'),
    path('cargar_index_y_BD/', views.cargar_index_y_BD, name='cargar_index_y_BD'),
    path('crear_index/', views.crear_index, name='crear_index'),
    path('buscar_titulo_o_descripcion/', views.buscar_titulo_o_descripcion, name='buscar_titulo_o_descripcion'),
    path('buscar_similares_generos/', views.buscar_similares_generos, name='buscar_similares_generos'),
    path('rate_pelicula/<int:pelicula_id>/', views.rate_pelicula, name='rate_pelicula'),
    path('recomendar_peliculas/', views.mostrar_usuarios_similares, name='mostrar_usuarios_similares'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('editar_usuario/', views.editar_usuario, name='editar_usuario'),
    path('', views.home, name='home')
    ]
