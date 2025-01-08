#encoding:utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection
from main.busquedaWoosh import *
from django.core.paginator import Paginator
from .models import Pelicula, Puntuacion, Usuario, User
from django.contrib.auth import login, authenticate, logout
from .forms import RegistroForm, LoginForm, EditarUsuarioForm
from django.db.models import F, Value, FloatField, ExpressionWrapper, Avg


GENEROS_CHOICES = [
        'Acción', 'Animación', 'Misterio', 'Bélica', 'Ciencia ficción', 'Comedia', 
        'Crimen', 'Drama', 'Suspense', 'Familia', 'Música', 'Romance', 'Terror', 
        'Western', 'Documental'
]

def mostrar_peliculas(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM main_pelicula")
        peliculas = cursor.fetchall()
        paginator = Paginator(peliculas, 21)  # Muestra 10 películas por página

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    return render(request, 'mostrar_peliculas.html', {'peliculas': page_obj})


def cargar_index_y_BD(request):
    return render(request, 'index_cargar.html')

def crear_index(request):
    crea_index()
    return render(request, 'index_cargar.html', {'peliculas': "peliculas cargadas satisfactoriamente"})

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

@login_required
def rate_pelicula(request, pelicula_id):
    pelicula = get_object_or_404(Pelicula, idPelicula=pelicula_id)
    usuario = get_object_or_404(Usuario, user=request.user.id)
    if request.method == 'POST':
        puntuacion = int(request.POST.get('puntuacion'))
        ratings = Puntuacion.objects.filter(idUsuario=usuario, idPelicula=pelicula)
        if ratings.exists():
            ratings.update(puntuacion=puntuacion)
        else:
            Puntuacion.objects.create(idUsuario=usuario, idPelicula=pelicula, puntuacion=puntuacion)
    return redirect('mostrar_peliculas')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def editar_usuario(request):
    usuario = request.user.usuario
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EditarUsuarioForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form})

def home(request):
    return render(request, 'home.html')

def mostrar_usuarios_similares(request):
    usuario = get_object_or_404(Usuario, user_id=request.user.id)

    # Asignar pesos a cada criterio
    peso_edad = 0.4
    peso_sexo = 0.2
    peso_ocupacion = 0.3
    peso_codigo_postal = 0.1

    # Calcular la similitud ponderada
    usuarios_similares = Usuario.objects.annotate(
        similitud=ExpressionWrapper(
            (Value(peso_edad, output_field=FloatField()) * (F('edad') == usuario.edad)) +
            (Value(peso_sexo, output_field=FloatField()) * (F('sexo') == usuario.sexo)) +
            (Value(peso_ocupacion, output_field=FloatField()) * (F('ocupacion') == usuario.ocupacion)) +
            (Value(peso_codigo_postal, output_field=FloatField()) * (F('codigoPostal') == usuario.codigoPostal)),
            output_field=FloatField()
        )
    ).exclude(user_id=usuario.user_id).order_by('-similitud')

    # Obtener las películas puntuadas por los usuarios similares
    peliculas_recomendadas = Puntuacion.objects.filter(
        idUsuario__in=usuarios_similares
    ).values('idPelicula').annotate(promedio_puntuacion=Avg('puntuacion')).order_by('-promedio_puntuacion')

    peliculas = Pelicula.objects.filter(idPelicula__in=[p['idPelicula'] for p in peliculas_recomendadas])

    return render(request, 'recomendar_peliculas_usuarios.html', {
        'usuarios': usuarios_similares,
        'usuario': usuario,
        'peliculas': peliculas,
        'peliculas_recomendadas': peliculas_recomendadas
    })


