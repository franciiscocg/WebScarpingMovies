#encoding:utf-8
from django.shortcuts import render, redirect
from django.db import connection
from main.busquedaWoosh import *

def mostrar_peliculas(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM main_pelicula")
        peliculas = cursor.fetchall()
    
    return render(request, 'mostrar_peliculas.html', {'peliculas': peliculas})

def cargar_index_y_BD(request):
    return render(request, 'index_cargar.html')

def crear_index(request):
    crea_index()
    return render(request, 'index_cargar.html')