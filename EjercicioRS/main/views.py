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
from django.db.models.functions import Abs, Power


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
    
    # Definir rangos máximos razonables para normalizar
    rango_edad = 100.0
    rango_codigo_postal = 10000.0
    
    # Calcular la similitud ponderada teniendo en cuenta las diferencias
    usuarios_similares = Usuario.objects.annotate(
        similitud=ExpressionWrapper(
            (Value(peso_edad, output_field=FloatField()) * (1 - Power(Abs(F('edad') - usuario.edad) / rango_edad, 2))) +
            (Value(peso_sexo, output_field=FloatField()) * (F('sexo') == usuario.sexo)) +
            (Value(peso_ocupacion, output_field=FloatField()) * (F('ocupacion') == usuario.ocupacion)) +
            (Value(peso_codigo_postal, output_field=FloatField()) * (1 - Power(Abs(F('codigoPostal') - usuario.codigoPostal) / rango_codigo_postal, 2))),
            output_field=FloatField()
        )
    ).exclude(user_id=usuario.user_id)
    
    # Crear un diccionario de similitudes para usar en el cálculo de promedios ponderados
    similitudes = {u.user_id: u.similitud for u in usuarios_similares}
    
    # Obtener todas las puntuaciones de los usuarios similares
    puntuaciones = Puntuacion.objects.filter(
        idUsuario__in=usuarios_similares
    ).select_related('idUsuario')
    
    # Calcular promedios ponderados por película
    peliculas_puntuaciones = {}
    for puntuacion in puntuaciones:
        id_pelicula = puntuacion.idPelicula_id
        if id_pelicula not in peliculas_puntuaciones:
            peliculas_puntuaciones[id_pelicula] = {
                'suma_ponderada': 0,
                'suma_pesos': 0
            }
        
        # Usar la similitud como peso para la puntuación
        peso = similitudes[puntuacion.idUsuario.user_id]
        peliculas_puntuaciones[id_pelicula]['suma_ponderada'] += puntuacion.puntuacion * peso
        peliculas_puntuaciones[id_pelicula]['suma_pesos'] += peso
    
    # Calcular el promedio final y ordenar las películas
    peliculas_recomendadas = []
    for id_pelicula, datos in peliculas_puntuaciones.items():
        if datos['suma_pesos'] > 0:  # Evitar división por cero
            promedio_ponderado = datos['suma_ponderada'] / datos['suma_pesos']
            peliculas_recomendadas.append({
                'idPelicula': id_pelicula,
                'promedio_puntuacion': promedio_ponderado
            })
    
    # Ordenar por promedio ponderado
    peliculas_recomendadas.sort(key=lambda x: x['promedio_puntuacion'], reverse=True)
    
    # Obtener los objetos Pelicula correspondientes
    ids_peliculas = [p['idPelicula'] for p in peliculas_recomendadas]
    peliculas = Pelicula.objects.filter(idPelicula__in=ids_peliculas)
    
    # Ordenar las películas según el orden de recomendación
    peliculas_ordenadas = sorted(
        peliculas,
        key=lambda x: ids_peliculas.index(x.idPelicula)
    )

    return render(request, 'recomendar_peliculas_usuarios.html', {
        'usuarios': usuarios_similares,
        'usuario': usuario,
        'peliculas': peliculas_ordenadas,
        'peliculas_recomendadas': peliculas_recomendadas
    })