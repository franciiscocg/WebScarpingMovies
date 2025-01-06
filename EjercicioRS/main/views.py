#encoding:utf-8
from django.shortcuts import render, redirect
from django.db import connection
from main.busquedaWoosh import *
GENEROS_CHOICES = [
        'Acción', 'Animación', 'Misterio', 'Bélica', 'Ciencia ficción', 'Comedia', 
        'Crimen', 'Drama', 'Suspense', 'Familia', 'Música', 'Romance', 'Terror', 
        'Western', 'Documental'
]

def mostrar_peliculas(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM main_pelicula")
        peliculas = cursor.fetchall()
    
    return render(request, 'mostrar_peliculas.html', {'peliculas': peliculas})

def cargar_index_y_BD(request):
    return render(request, 'index_cargar.html')

def crear_index(request):
    crea_index()
    return render(request, 'index_cargar.html', {'peliculas': "peliculas cargadas satisdactoriamente"})

def buscar_titulo_o_descripcion(request):
    peliculas = []
    if request.method == 'POST':
        busqueda = request.POST.get('query', '')  # Búsqueda de texto
        idioma = request.POST.get('idioma', '')  # Filtro de idioma
        generos = request.POST.getlist('genero')  # Filtro de géneros (lista)
        min_nota = request.POST.get('min_nota', '')  # Mínima valoración
        max_nota = request.POST.get('max_nota', '')  # Máxima valoración

        # Validar que los géneros estén en la lista permitida
        generos = [genero for genero in generos if genero in GENEROS_CHOICES]

        peliculas = filtrar_peliculas(busqueda, idioma, generos, min_nota, max_nota)

    return render(request, 'buscador.html', {'peliculas': peliculas, 'generos': GENEROS_CHOICES})

def buscar_similares_generos(request):
    peliculas = []
    if request.method == 'POST':
        busqueda = request.POST.get('query', '')  # Búsqueda de texto

        # Buscar la película por título
        with connection.cursor() as cursor:
            cursor.execute("SELECT genero FROM main_pelicula WHERE titulo = %s", [busqueda])
            result = cursor.fetchone()
        
        if result:
            generos = result[0].split(',')  # Asumiendo que los géneros están separados por comas

            # Filtrar películas con los mismos géneros
            if generos:
                query = """
                    SELECT idPelicula, titulo, imagen, descripcion, nota, genero, date, link, idiomas
                    FROM main_pelicula
                    WHERE """ + " OR ".join(["genero LIKE %s"] * len(generos))
                with connection.cursor() as cursor:
                    cursor.execute(query, [f'%{genero}%' for genero in generos])
                    peliculas = cursor.fetchall()

    return render(request, 'buscador_similares.html', {'peliculas': peliculas})

def home(request):
    return render(request, 'home.html')