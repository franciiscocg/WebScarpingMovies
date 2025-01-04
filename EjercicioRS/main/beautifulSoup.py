#encoding:utf-8
from web import login
import requests
import sqlite3
from bs4 import BeautifulSoup
import os, ssl
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
    
    ruta_carpeta_data = os.path.join(os.path.dirname(__file__), '..')
    ruta_bd = os.path.join(ruta_carpeta_data, 'db.sqlite3')
    conn = sqlite3.connect(ruta_bd)
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS main_pelicula") 
    conn.execute('''CREATE TABLE main_pelicula
       (IDPELICULA      INTEGER PRIMARY KEY AUTOINCREMENT,
        TITULO          TEXT    NOT NULL,
        IMAGEN        TEXT    ,
       DESCRIPCION      TEXT  ,
        NOTA          INTEGER,
       GENERO        TEXT   ,
       DATE        TEXT,
       LINK        TEXT NOT NULL,
       IDIOMAS     TEXT);''')
    
    l = extraer_peliculas()

    for p in l:
        titulo = p.find("h3").string
        link = "https://playdede.me/" + p.find("a")["href"]
        imagen = p.find("img")["src"]
        genero = p.find("div", class_="data").span.string
        date = p.find("div", class_="data").p.string

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

        print(titulo, imagen, descripcion, nota, genero, date, link, idiomas)
        conn.execute("""INSERT INTO main_pelicula VALUES (?,?,?,?,?,?,?,?,?)""",(None,titulo, imagen, descripcion, nota, genero, date, link, idiomas))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    almacenar_bd()