# Librerias estandar.
import concurrent.futures

# Librerias de terceros.
import numpy as np
import pandas as pd

# Dependencias.
from .constantes import Tipo_Operacion
from .decoradores import time_it


def Ie(
    frecuencias: 'pd.Series',
    operacion: 'Tipo_Operacion'
) -> 'pd.Series':
    '''
        Calcula la informaicon mutua de un conjunto
        retorna la sumatoria de esta y el valor por dato.
    '''

    # Se obtiene cual es el operdor del logaritmo a usar.
    if operacion is Tipo_Operacion.CUANTIFICABLE:
        log = np.log10
    elif operacion is Tipo_Operacion.TRANSMISION_DATOS:
        log = np.log2
    elif operacion is Tipo_Operacion.TRANSICION_ESTADOS:
        log = np.log
    else:
        raise Exception('El tipo de operación no es valido')

    informacion_mutua = -log(frecuencias)

    return informacion_mutua


def He(
    frecuencias: 'pd.Series',
    informacion_mutua: 'pd.Series',
) -> 'pd.Series':
    '''
        Calcula la entropia de un conjunto
        retorna la sumatoria de esta y el valor por dato.
    '''
    entropia = frecuencias * informacion_mutua

    return entropia


def pre_analisis(
    texto: str
) -> 'tuple[pd.Series, pd.Series]':
    '''
        Realiza un pre-análisis del texto, retorna
        la frecuencia y el alfabeto del texto.
    '''

    frecuencias = pd.Series(dtype=np.float64)
    alfabeto = pd.Series(dtype=str)

    i = 0
    for caracter in texto:
        if caracter not in alfabeto.index:
            id = 'S{}'.format(i)

            alfabeto[caracter] = id

            frecuencias[id] = 1

            i += 1

        else:
            id = alfabeto[caracter]
            frecuencias[id] += 1

    return alfabeto, frecuencias


def multi_pre_analisis(
    texto: str,
    procesos: int,
) -> 'tuple[pd.Series, pd.Series]':
    '''
        Realiza la operación de pre-análisis del texto
        utilizando multiprocesos.
    '''

    # Primero separamos los recursos para repartirlo equitativamente entre los procesos.
    longitud_texto = len(texto)

    # Secciones de texto.
    secciones = int(longitud_texto / procesos)

    # Paquetes de datos.
    paquetes = []

    # Creamos los paquetes de datos que se parasaran a los procesos.
    a = 0
    b = secciones
    for _ in range(procesos):
        paquetes.append(texto[a:b])
        a += secciones
        b += secciones

    # Creamos un contexto con el ejecutador de los procesos.
    with concurrent.futures.ProcessPoolExecutor() as ejecutador:
        # Instanciamos un generador multiproceso con map.
        resultados = ejecutador.map(pre_analisis, paquetes)

    # Ahora juntamos las frecuencias y los alfabetos que
    # cada proceso utilizo.
    alfabeto = pd.Series()
    frecuencias = pd.Series()

    # Conteo de los id's.
    conteo_id = 0

    # Por cada resultado, se agrega al buffer.
    for resultado in resultados:
        # Recuperamos la frecuencia y alfabeto.
        A, F = resultado

        for id_c, caracter in zip(A, A.index):
            if caracter not in alfabeto.index:
                id = 'S{}'.format(conteo_id)
                alfabeto[caracter] = id
                frecuencias[id] = F[id_c]

                conteo_id += 1

            else:
                id = alfabeto[caracter]
                frecuencias[id] += F[id_c]

    return frecuencias, alfabeto
