#encoding:latin-1
import os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, NUMERIC, TEXT, KEYWORD, DATETIME
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Term, NumericRange, And, Or
from main.beautifulSoup import almacenar_bd

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

    
def filtrar_peliculas(busqueda, idioma, generos, min_nota, max_nota):
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        # Crear consultas
        query_parts = []

        # Búsqueda general (título o descripción)
        if busqueda:
            query_parts.append(
                MultifieldParser(["titulo", "descripcion"], ix.schema).parse(f"{busqueda}*")
            )

        # Filtro de idioma
        if idioma in ['esp', 'espsub', 'lat', 'engsub', 'eng']:
            query_parts.append(Term("idioma", idioma))

        if generos:
            genero_queries = [Term("genero", genero) for genero in generos]
            query_parts.append(Or(genero_queries))

        # Filtro de rango de valoración
        if min_nota or max_nota:
            min_val = float(min_nota) if min_nota else 0.0
            max_val = float(max_nota) if max_nota else 10.0
            query_parts.append(NumericRange("nota", min_val, max_val))

        # Combinar todas las consultas
        final_query = And(query_parts) if query_parts else None

        # Realizar la búsqueda
        results = searcher.search(final_query, limit=50) if final_query else []

        # Construir la lista de resultados
        result_list = []
        for result in results:
            result_list.append([
                result.get("titulo", ""),
                result.get("descripcion", ""),
                result.get("nota", ""),
                result.get("genero", ""),
                result.get("date", ""),
                result.get("idioma", ""),
            ])
        return result_list