'''
    Estructura de un arbol binario simple
    usado principalmente en la codificacion de huffman
'''


# Librerias Propias.
from .nodo import Nodo_Binario


class Arbol_Binario(dict):

    def __init__(self) -> None:
        # Raiz del arbol binario.
        self.raiz = None

        # Total de nodos en el arbol binario.
        self.total_nodos = 0

        # Coteo de id's
        self.conteo_id = 0

    def __str__(self) -> str:
        # Representacion en string del arbol.
        mensaje = 'Total de nodos: {}\n'.format(self.total_nodos)

        for id_nodo in self:
            mensaje += str(self[id_nodo]) + '\n'

        return mensaje

    def esta_vacio(self) -> bool:
        # Indica si el arbol esta vacio.
        return True if self.total_nodos <= 0 else False

    def flush(self) -> None:
        # Restablece el arbol a un estado vacio, eliminando
        # todos los nodos
        self.total_nodos = 0
        self.raiz = None        
        self.clear()

    def agregar_nodo(
        self,
        valor: 'int | float',
        id: 'int | str' = None,
        *args,
        **kwargs
    ) -> None:
        # Agrega un nodo de manera sistematica al
        # arbol binario.
        kwargs['valor'] = valor

        # Si no se agrega un id, entonces se auto_asigna uno.
        if id is None:
            # Si el id esta asignado, se busca uno disponible.
            id = self.conteo_id

            while id in self:
                self.conteo_id += 1
                id = self.conteo_id

        self[id] = Nodo_Binario(id, **kwargs)

        # Si el arbol esta vacio entonces el nodo se agrega
        # como raiz.
        if self.esta_vacio():
            self.raiz = id

        else:
            # Si el arbol no esta vacio, buscamos el lugar en el
            # que pertenece el nodo.
            puntero = self.raiz
            nodo: Nodo_Binario = self[puntero]

            # Mientras que el nodo no sea una hoja, realizamos
            # una busqueda binaria
            while not nodo.es_hoja():
                if valor < nodo.propiedades['valor']:
                    puntero = nodo.hijo_izquierda
                else:
                    puntero = nodo.hijo_derecha

                # Si el nodo no es hoja, entonces se termina el ciclo.
                if puntero is None:
                    break

                nodo = self[puntero]

            # Agregamos el nodo al arbol.
            if valor < nodo.propiedades['valor']:
                nodo.hijo_izquierda = id

            else:
                nodo.hijo_derecha = id

        self.total_nodos += 1