#encoding:utf-8
from web import login
import requests
import sqlite3
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re
import os, ssl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def extraer_peliculas():

    cookies = login()
    headers = {'PLAYDEDE_SESSION': cookies[0],
               'cf_clearance': cookies[1],
               'utoken': cookies[2]}
    
    url = "https://playdede.me/peliculas/1"
    response = requests.get(url, cookies=headers)
    page_source = response.text
    
    s = BeautifulSoup(page_source, "lxml")
    l = s.find_all("article", class_="item tvshows")
    return print(l)

def almacenar_bd():
    conn = sqlite3.connect('as.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS PELICULAS") 
    conn.execute('''CREATE TABLE PELICULAS
       (PELICULA       INTEGER NOT NULL,
       TITULO          TEXT    NOT NULL,
       DESCRIPCION      TEXT    NOT NULL,
       GENERO        TEXT    NOT NULL,
       DATE        TEXT NOT NULL,
       IDIOMAS           TEXT);''')
    l = extraer_peliculas()
    for i in l:
        jornada = int(re.compile('\d+').search(i['id']).group(0))
        partidos = i.find_all("tr",id=True)
        for p in partidos:
            equipos= p.find_all("span",class_="nombre-equipo")
            local = equipos[0].string.strip()
            visitante = equipos[1].string.strip()
            resultado_enlace = p.find("a",class_="resultado")
            goles=re.compile('(\d+).*(\d+)').search(resultado_enlace.string.strip())
            goles_l=goles.group(1)
            goles_v=goles.group(2)
            link = resultado_enlace['href']
                
            conn.execute("""INSERT INTO PELICULAS VALUES (?,?,?,?,?,?)""",(jornada,local,visitante,goles_l,goles_v,link))
    conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM PELICULAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

if __name__ == "__main__":
    extraer_peliculas()