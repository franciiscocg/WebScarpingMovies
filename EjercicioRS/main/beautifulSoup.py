#encoding:utf-8
from main.web import login
import requests
import sqlite3
from bs4 import BeautifulSoup
import os, ssl
from datetime import datetime
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

cookies = login()

def extraer_peliculas():
    
    url = "https://playdede.me/peliculas/1"
    response = requests.get(url, cookies=cookies).text
    s = BeautifulSoup(response, "lxml")
    l = s.find_all("article", class_="item tvshows", id=True)
    return l

def almacenar_bd():

    lista = []
    ruta_carpeta_data = os.path.join(os.path.dirname(__file__), '..')
    ruta_bd = os.path.join(ruta_carpeta_data, 'db.sqlite3')
    conn = sqlite3.connect(ruta_bd)
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS main_pelicula")
    conn.execute("DROP TABLE IF EXISTS main_puntuacion")
    conn.execute('''CREATE TABLE main_pelicula
       (IDPELICULA      INTEGER PRIMARY KEY AUTOINCREMENT,
        TITULO          TEXT    NOT NULL,
        IMAGEN        TEXT    ,
       DESCRIPCION      TEXT  ,
        NOTA          REAL    ,
       GENERO        TEXT   ,
       DATE        DATE    ,
       LINK        TEXT NOT NULL,
       IDIOMAS     TEXT);''')
    
    conn.execute('''CREATE TABLE main_puntuacion
         (IDPUNTUACION      INTEGER PRIMARY KEY AUTOINCREMENT,
          IDPELICULA          INTEGER    NOT NULL,
          IDUSUARIO          INTEGER    NOT NULL,
          PUNTUACION          INTEGER    NOT NULL,
          FOREIGN KEY (IDPELICULA) REFERENCES main_pelicula(IDPELICULA),
          FOREIGN KEY (IDUSUARIO) REFERENCES auth_user(id));''')
    
    l = extraer_peliculas()

    for p in l:
        titulo = p.find("h3").string
        link = "https://playdede.me/" + p.find("a")["href"]
        imagen = p.find("img")["src"]
        genero = p.find("div", class_="data").span.string
        if genero !=None:
            genero = genero.replace(" /", ",")
        date = p.find("div", class_="data").p.string
        date = formatear_fecha(date)
        datos_pelicula = requests.get(link, cookies=cookies).text
        s = BeautifulSoup(datos_pelicula, "lxml")
        descripcion = s.find("div", class_="overview").p.string
        nota = s.find("div", class_="nota").span.text.split(" ")[0]
        idiomas = []
        language_selector = s.find_all("div", class_="languageSelector")
        for selector in language_selector:
            imgs = selector.find_all("img")
            for img in imgs:
                # Extrae el valor del atributo 'data-lang' si existe
                data_lang = img.get("data-lang")
                if data_lang:
                    idiomas.append(data_lang)
        idiomas = ','.join(idiomas)

        lista.append((titulo, descripcion, float(nota), genero, date, idiomas))
        conn.execute("""INSERT INTO main_pelicula VALUES (?,?,?,?,?,?,?,?,?)""",(None,titulo, imagen, descripcion, nota, genero, date, link, idiomas))
        

    conn.commit()
    conn.close()
    return lista

def formatear_fecha(fecha):
    fecha = fecha.replace("Dic.", "12").replace("Ene.", "01").replace("Feb.", "02").replace("Mar.", "03").replace("Abr.", "04").replace("May.", "05").replace("Jun.", "06").replace("Jul.", "07").replace("Ago.", "08").replace("Sep.", "09").replace("Oct.", "10").replace("Nov.", "11")
    fecha = fecha.replace(",", "")
    fecha = datetime.strptime(fecha, "%m %d %Y")
    return fecha
   
