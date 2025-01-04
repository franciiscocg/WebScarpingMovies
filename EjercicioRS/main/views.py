#encoding:utf-8
from django.shortcuts import render
from django.db import connection

def mostrar_peliculas(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PELICULAS")
        peliculas = cursor.fetchall()
    
    return render(request, 'mostrar_peliculas.html', {'peliculas': peliculas})