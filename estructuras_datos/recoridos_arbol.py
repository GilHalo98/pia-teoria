'''
    Metodos de exploracion o busqueda de arboles.
'''


# Librerias estandar.
import copy
from typing import Generator

# Dependencias
from .arbol_binario import Arbol_Binario
from .nodo import Nodo_Binario


def expandir_nodo(
    nodo: Nodo_Binario,
    visitados: 'list[str | int]'
) -> 'list[str | int]':
    # Verificamos que los nodos en la expancion no estan repetidos
    # aquel nodo repetido es descartado de la expancion.
    expancion = []
    for id_expancion in nodo.get_hijos():
        if id_expancion not in visitados and id_expancion is not None:
            expancion.append(id_expancion)

    return expancion


def DFS(arbol: Arbol_Binario) -> 'Generator[list[str | int], None, None]':
    # Recorre el arbol con el algorito Deep Search First.

    # Pila de recorridos.
    pila_recorrido = []

    # Lista de nodos visitados.
    visitados = []

    # Puntero de busqueda.
    puntero = arbol.raiz

    # Paramos cuando el puntero sea Nulo.
    while puntero is not None:
        # Insanciamos el nodo actual.
        nodo_actual: Nodo_Binario = arbol[puntero]

        # Realizamos la expancion del nodo.
        expancion = expandir_nodo(nodo_actual, visitados)

        # Agregamos el id del nodo actual a la pila del recorrido.
        if puntero not in pila_recorrido:
            pila_recorrido.append(puntero)

        # Marcamos el nodo actual como visitado.
        if puntero not in visitados:
            visitados.append(puntero)

        # Si la expancion no esta vacia.
        if len(expancion) > 0:
            # Actualizamos el puntero a uno de
            # los hijos del nodo actual.
            puntero = expancion[0]

        # Si la expancion esta vacia.
        else:
            # En este punto encontramos o una hoja o un nodo explorado
            # en su totalidad.
            yield copy.deepcopy(pila_recorrido)

            # Realizamos un pop a la pila y actualizamos puntero.
            pila_recorrido.pop(-1)

            # Contamos los nodos en la pila de recorrido.
            long_recorrido = len(pila_recorrido)

            # Si la pila de recorrido tiene un nodo, entonces se
            # continua con la exploracion, sino se termina.
            puntero = pila_recorrido[-1] if long_recorrido > 0 else None