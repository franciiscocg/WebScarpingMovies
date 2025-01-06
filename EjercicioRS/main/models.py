#encoding:utf-8

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Ocupacion(models.Model):
    ocupacionId = models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name='Ocupación', unique=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ('nombre', )

class Usuario(models.Model):
    idUsuario = models.AutoField(primary_key=True)
    edad = models.IntegerField(verbose_name='Edad', help_text='Debe introducir una edad')
    sexo = models.CharField(max_length=1, verbose_name='Sexo', help_text='Debe elegir entre M o F')
    ocupacion = models.ForeignKey(Ocupacion, on_delete=models.SET_NULL, null=True)
    codigoPostal = models.TextField(verbose_name='Código Postal')

    def __str__(self):
        return self.idUsuario
    
    class Meta:
        ordering = ('idUsuario', )

class Genero(models.Model):
    GENEROS_CHOICES = [
        'Acción', 'Animación', 'Misterio', 'Bélica', 'Ciencia ficción', 'Comedia', 
        'Crimen', 'Drama', 'Suspense', 'Familia', 'Música', 'Romance', 'Terror', 
        'Western', 'Documental'
    ]
    idGenero = models.AutoField(primary_key=True)
    nombre = models.TextField(unique=True)
    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering =('nombre', )


class Idioma(models.Model):
    IDIOMAS_CHOICES = ['esp', 'espsub', 'lat', 'engsub', 'eng']
    idIdioma = models.AutoField(primary_key=True)
    nombre = models.TextField(max_length=10,unique=True)
    

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ('nombre', )

class Pelicula(models.Model):
    idPelicula = models.AutoField(primary_key=True)
    titulo = models.TextField()
    imagen = models.URLField()
    descripcion = models.TextField()
    nota = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    genero = models.TextField()
    date = models.DateField()
    link = models.URLField()
    idiomas = models.TextField()
    puntuaciones = models.ManyToManyField(Usuario, through='Puntuacion')

    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ('titulo', 'date', )

class Puntuacion(models.Model):
    PUNTUACIONES = ((1, 'Muy mala'), (2,'Mala'), (3,'Regular'), (4,'Buena'), (5,'Muy Buena'))
    idUsuario = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    idPelicula = models.ForeignKey(Pelicula,on_delete=models.CASCADE)
    puntuacion = models.IntegerField(verbose_name='Puntuación', validators=[MinValueValidator(0), MaxValueValidator(5)], choices=PUNTUACIONES)
    
    def __str__(self):
        return (str(self.puntuacion))
    
    class Meta:
        ordering=('idPelicula','idUsuario', )