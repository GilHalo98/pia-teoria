# Librerias de terceros.
from graphviz import Graph

# Librerias propias.
from util.constantes import SIMBOLOS_ESPECIALES
from estructuras_datos.nodo import Nodo_Binario
from estructuras_datos.arbol_binario import Arbol_Binario


def graficar_arbol_binario(
    arbol: 'Arbol_Binario',
    archivo_salida: str
) -> None:
    grafico = Graph(
        comment='Test',
        format='svg',
    )

    grafico.node_attr['shape'] = 'circle'

    for id_nodo in arbol:
        nodo: Nodo_Binario = arbol[id_nodo]

        if not nodo.es_hoja():
            # Se agrega el nodo en el grafico.
            label = '{id: ' + str(nodo.id_nodo) + '}|'
            label += '{sigma: ' + str(nodo.propiedades['valor']) + '}'

            grafico.node(
                str(nodo.id_nodo),
                label=label,
                shape='Mrecord'
            )

            if nodo.hijo_izquierda is not None:
                # Hijo de la izquierda.
                grafico.edge(
                    str(nodo.id_nodo),
                    str(nodo.hijo_izquierda),
                    str(nodo.costo_izquierda)
                )

            if nodo.hijo_derecha is not None:
                # Hijo de la derecha.
                grafico.edge(
                    str(nodo.id_nodo),
                    str(nodo.hijo_derecha),
                    str(nodo.costo_derecha)
                )

        else:
            # Si el nodo es una hoja, se agrega tambien su caracter.
            label = '{id: ' + str(nodo.id_nodo) + '}|{'
            label += 'frecuencia: ' + str(nodo.propiedades['valor'])

            simbolo = str(nodo.propiedades['simbolo'])

            if simbolo in SIMBOLOS_ESPECIALES:
                label += '|simbolo: \\' + simbolo + '}'

            else:
                label += '|simbolo: ' + simbolo + '}'

            grafico.node(
                str(nodo.id_nodo),
                label=label,
                shape='Mrecord'
            )


    # Por ultimo renderiza el grafo en un archivo svg.
    # grafico.attr(overlap='false', compound='true')
    grafico.render(filename=archivo_salida)