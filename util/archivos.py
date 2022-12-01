'''
    Funciones de IO de archivos para las instancias
    del programa princpial.

    Ideas para usar multiprocesos:
        En los archivos de formato txt se pueden cargar sin impactar
        en el tiempo de ejecución, separar el texto en paquetes y pasarlos
        al pool de procesos para la frecuencia y el alfabeto
        (tecnicamente esta idea ya esta implementada).

        En los archivos de format pdf se puede pasar las paginas seccionadas
        para cada proceso, realizariamos el mismo proceso que con los
        archivos de formato txt, solo que aquí no se mantendira en
        memoria todo el texto del documento pdf.
'''


# Librerias estandar.
import pathlib
import datetime
import concurrent.futures

# Liberias de terceros.
import PyPDF2
import numpy as np
import pandas as pd

# Librerias propias.
from .decoradores import time_it
from .constantes import FORMATOS_VALIDOS


def nombre_generico(nombre_base: str) -> str:
    '''
        Genera un nombre generico para el archivo.
    '''
    hoy = datetime.datetime.now()

    archivo_salida = '{}-{}{}{}{}'.format(
        nombre_base,
        hoy.day,
        hoy.hour,
        hoy.minute,
        hoy.second
    )

    return archivo_salida


def iterador_archivo(
    dir: 'str | pathlib.Path'
) -> 'Generator[str, None, None]':
    '''
        Verifica la existencia del archivo, así como si el formato
        es valido y retorna un generador que itera por cada caracter
        del archivo.
    '''
    # Si la dirección al archivo es de tipo string, entonces se
    # convierte a un patlib object.
    if type(dir) == str:
        dir = pathlib.Path(dir)

    # Si no es un archivo, entonces levanta una excepcion.
    if not dir.is_file():
        raise Exception('{} no es un archivo'.format(dir))

    # Recuperamos el formato del archivo.
    formato_archivo = dir.suffix.lower()

    # Si el formato del archivo no es valido, levanta una excepcion.
    if formato_archivo not in FORMATOS_VALIDOS:
        raise Exception('{} no es de tipo {}'.format(dir, FORMATOS_VALIDOS))

    if formato_archivo == FORMATOS_VALIDOS[0]:
        # Si el archivo es de formato PDF.
        pass

    if formato_archivo == FORMATOS_VALIDOS[0]:
        # Si el archivo es de formato PDF.
        # Instanciamos el objeto archivo.
        objeto_archivo = PyPDF2.PdfFileReader(dir)

        # Iteramos por cada pagina.
        for pagina in range(objeto_archivo.numPages):
            # Recuperamos un objeto pagina.
            objeto_pagina = objeto_archivo.getPage(pagina)

            # La concatenamos al texto.
            pagina = objeto_pagina.extractText()

            # Por cada caracter en la linea.
            for caracter in pagina:
                # Retornamos el caracter.
                yield caracter

    elif formato_archivo == FORMATOS_VALIDOS[1]:
        # Si el archivo es de formato TXT.
        # Instanciamos el objeto archivo.
        with open(dir, 'r', encoding='utf-8') as objeto_archivo:
            # Por cada linea el el archivo.
            for linea in objeto_archivo:
                # Por cada caracter en la linea.
                for caracter in linea:
                    # Retornamos el caracter.
                    yield caracter


@time_it
def analizar_archivo(
    dir: 'str | pathlib.Path',
) -> 'tuple[pd.Series, pd.Series]':
    # Frecuencias del medio.
    frecuencias = pd.Series(dtype=np.float64)

    # Alfabeto del medio.
    alfabeto = pd.Series(dtype=str)

    # Iterador del contenido del archivo.
    archivo = iterador_archivo(dir)

    # Por cada caracter en el archivo.
    conteo_id = 0
    for caracter in archivo:
        # Verificamos si el caracter
        # no tiene un id asignado.
        if caracter not in alfabeto.index:
            # Se asigna un id al caracter.
            id = 'S{}'.format(conteo_id)

            # Se agrega al alfabeto.
            alfabeto[caracter] = id

            # Se agrega a las frecuencias.
            frecuencias[id] = 1

            conteo_id += 1

        else:
            # Si el caracter ya tiene
            # un id asignado.

            # Consultamos su id.
            id = alfabeto[caracter]

            # Agregamos 1 a la frecuencia del caracter.
            frecuencias[id] += 1

    return frecuencias, alfabeto