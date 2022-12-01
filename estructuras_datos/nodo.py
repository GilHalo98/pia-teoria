"""
    Clase nodo para un arbol binario.
"""


# Clase nodo contenida en el arbol de combinaciones.
class Nodo_Binario(object):
    """
        Clase nodo para un arbol binario, contiene el padre, el hijo a
        la izquierda y la derecha, así como sus respectivos pesos.

        Contiene el contenido del nodo y un id del mismo. Funciones para
        saber si es hoja o raiz.
    """

    # Constructor de clase.
    def __init__(
        self,
        id_nodo: 'int | str',
        padre: 'int | str | None' = None,
        hijo_izquierda: 'int | str | None' = None,
        hijo_derecha: 'int | str | None' = None,
        costo_izquierda: 'int | float' = 0,
        costo_derecha: 'int | float' = 1,
        *args,
        **kwargs
    ) -> None:
        # Id del nodo.
        self.id_nodo = id_nodo

        # Id del padre del nodo.
        self.padre = padre

        # Id de conexiones del nodo.
        self.hijo_izquierda = hijo_izquierda
        self.hijo_derecha = hijo_derecha

        # Costo de las conexiones.
        self.costo_izquierda = costo_izquierda
        self.costo_derecha = costo_derecha

        # Propiedades.
        self.propiedades = kwargs

    def __str__(self) -> str:
        mensaje = 'id: {}, contenido: {}'.format(
            self.id_nodo,
            self.propiedades
        )

        if not self.es_raiz():
            mensaje += ', padre: {}'.format(
                self.padre
            )

        if not self.es_hoja():
            mensaje += ', hijo izquierda: {} hijo derecha: {}'.format(
                self.hijo_izquierda,
                self.hijo_derecha,
            )

        return mensaje

    def get_hijos(self) -> 'list[int | str]':
        return [self.hijo_izquierda, self.hijo_derecha]

    def es_hoja(self) -> bool:
        if self.hijo_izquierda is None and self.hijo_derecha is None:
            return True
        return False

    def es_raiz(self):
        return True if self.padre is None else False

    def costo_hacia(self, id_hijo: 'str | int') -> 'int | float':
        if id_hijo == self.hijo_izquierda:
            return self.costo_izquierda

        elif id_hijo == self.hijo_derecha:
            return self.costo_derecha

        raise Exception('Hijo con id {} no existe!'.format(id_hijo))

