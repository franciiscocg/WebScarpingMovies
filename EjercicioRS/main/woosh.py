#encoding:latin-1
import os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, NUMERIC, TEXT, KEYWORD, DATETIME
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query
from beautifulSoup import almacenar_bd

index_dir = os.path.join("EjercicioRS", "Index")
#Crea un indice desde los documentos contenidos en dirdocs
#El indice lo crea en el directorio dirindex 
def crea_index():
    schem = Schema(titulo=TEXT(stored=True),
                   descripcion=TEXT(stored=True),
                   nota=NUMERIC(stored=True,numtype=float), 
                   genero=KEYWORD(stored=True, commas=True), 
                   date=DATETIME(stored=True), 
                   idioma=KEYWORD(stored=True, commas=True))

    #eliminamos el directorio del Ã­ndice, si existe
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
    os.mkdir(index_dir)
    
    #creamos el Ã­ndice
    ix = create_in(index_dir, schema=schem)
    #creamos un writer para poder aÃ±adir documentos al indice
    writer = ix.writer()
    i=0
    lista=almacenar_bd()
    for j in lista:
        #aÃ±ade cada juego de la lista al Ã­ndice
        writer.add_document(titulo=str(j[0]), descripcion=str(j[1]), nota=float(j[2]), genero=str(j[3]), date=j[4], idioma=str(j[5]))    
        i+=1
    writer.commit()  

    
def titulo_o_descripcion(palabra):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = MultifieldParser(["titulo", "descripcion"], ix.schema).parse(palabra)
        results = searcher.search(query)
        result_list = []
        for result in results:
            result_list.append(result)
        return result_list

def genero(palabra):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("genero", ix.schema).parse(palabra)
        results = searcher.search(query)
        result_list = []
        for result in results:
            result_list.append(result)
        return result_list
    
def nota(nota):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("nota", ix.schema).parse(nota)
        results = searcher.search(query)
        result_list = []
        for result in results:
            result_list.append(result)
        return result_list

def idioma(palabra):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        query = QueryParser("idioma", ix.schema).parse(palabra)
        results = searcher.search(query)
        result_list = []
        for result in results:
            result_list.append(result)
        return result_list 
        
    
        

if __name__ == "__main__":
    crea_index()