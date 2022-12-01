"""
    Arbol de Hunffman, es un arbol binario modificado.
"""


# Librerias estandar.
import time
import copy
import random
import pickle
import pathlib
import itertools

# Librerias Propias
from util.decoradores import time_it
from util.archivos import iterador_archivo
from estructuras_datos.nodo import Nodo_Binario
from estructuras_datos.recoridos_arbol import DFS
from estructuras_datos.arbol_binario import Arbol_Binario

# Librerias de terceros.
import bitarray
import numpy as np
import pandas as pd


class Arbol_Huffman(Arbol_Binario):

    def __init__(
        self,
        alfabeto: 'pd.DataFrame',
        frecuencias: 'pd.DataFrame'
    ) -> None:
        # Constructor de la clase padre.
        super().__init__()

        def contador() -> int:
            i = 0
            while True:
                yield i
                i += 1

        self.contar = contador()

        # Log de las operaciones que el algoritmo realiza.
        self.log = {
            self.contar.__next__(): 'Instancia cargada'
        }

        # Frecuencias originales de entrada del abecedaio.
        self.org_frecuencias = copy.deepcopy(
            frecuencias
        )

        # Alfabeto del esquema.
        self.alfabeto = alfabeto

        if len(self.alfabeto) > 0:
            self.log[
                self.contar.__next__()
            ] = 'Alfabeto cargado\n{}'.format(
                self.alfabeto.to_string()
            )

        # Frecuencias del esquema.
        self.frecuencias = frecuencias

        if len(self.frecuencias) > 0:
            self.log[
                self.contar.__next__()
            ] = 'Frecuencias cargadas\n{}'.format(
                self.frecuencias.to_string()
            )
        

        # Tabla de frecuencias de sigmas.
        self.frecuencias_sigma = pd.Series(dtype=np.float64)

        # Tabla de codificaciones.
        self.tabla_codificacion = pd.Series(dtype=str)

    def __construir_arbol_binario(self) -> None:
        # Se construye el arbol binario desde la parte inferior, o
        # los nodos hasta la raiz.
        # Limpiamos el arbol binario.
        self.flush()

        # Limpiamos tambien la tabla de codificacion.
        self.tabla_codificacion = pd.Series(dtype=str)

        # Limpiamos la tabla de frecuencias sigma.
        self.frecuencias_sigma = pd.Series(dtype=np.float64)

        # Instanciamos un zip con el simbolo y el id del simbolo.
        simbolo_id = zip(
            self.alfabeto.index,
            self.alfabeto
        )

        # Agregamos las hojas al arbol binario.
        for simbolo, id_hoja in simbolo_id:
            self[id_hoja] = Nodo_Binario(
                id_hoja,
                valor=self.frecuencias[id_hoja],
                simbolo=simbolo
            )

        # Primero creamos una copia auxiliar de las frecuencias.
        frecuencias_aux = self.frecuencias.copy()

        # Organizamos las frecuencias de manera decendente.
        frecuencias_aux.sort_values(ascending=True, inplace=True)

        # Ahora construimos el arbol desde las hojas hasta la raiz.
        s = 0
        while not frecuencias_aux.empty:
            # Extraemos los simbolos con menor frecuencia.
            simbolo_a = frecuencias_aux.index[0]
            simbolo_b = frecuencias_aux.index[1]

            # Calculamos su sigma, una suma de las frecuencias de ambos
            # simbolos.
            id_sigma = 'N{}'.format(s)
            sigma = frecuencias_aux[simbolo_a] + frecuencias_aux[simbolo_b]

            # Se agrega el sigma a una tabla de frecuencias de sigma.
            self.frecuencias_sigma[id_sigma] = sigma
            self.frecuencias[id_sigma] = sigma

            # Se agrega el sigma como una frecuencia en la
            # tabla de frecuencias auxiliar.
            frecuencias_aux[id_sigma] = sigma

            # Agregamos el nodo del sigma con correspondencia a su
            # frecuencia calculada.
            if self.frecuencias[simbolo_a] > self.frecuencias[simbolo_b]:
                id_der = simbolo_a
                id_izq = simbolo_b

            else:
                id_der = simbolo_b
                id_izq = simbolo_a

            # Actualizamos la conexion del padre de los hijos del nodo
            # sigma.
            self[id_izq].padre = id_sigma
            self[id_der].padre = id_sigma

            # Agregamos el nodo sigma al arbol.
            self[id_sigma] = Nodo_Binario(
                id_sigma,
                hijo_izquierda=id_izq,
                hijo_derecha=id_der,
                valor=sigma
            )

            # Eliminamos las frecuencias seleccionadas de la tabla de
            # frecuencias auxiliar.
            frecuencias_aux.pop(simbolo_a)
            frecuencias_aux.pop(simbolo_b)

            # Si existe un unico elemento, eso quiere decir que
            # encontramos la raiz.
            if len(frecuencias_aux) <= 1:
                break

            # Organizamos las frecuencias de manera decendente.
            frecuencias_aux.sort_values(ascending=True, inplace=True)

            # Aumentamos el conteo de sigmas.
            s += 1

        # El ultimo sigma calculado es la raiz del arbol.
        self.raiz = id_sigma

        # Se cuentan el total de nodos en el arbol.
        self.total_nodos = len(self)

        # Restablecemos las frecuencias originales.
        self.frecuencias = self.org_frecuencias.copy()

    def generar_tabla_codigos(self) -> None:
        # Se genera la tabla de codificacion del esquema.

        # Generamos el arbol binario.
        self.__construir_arbol_binario()

        # indicamos el recorrido a usar para crear la tabla, en este 
        # se usara DFS.
        recorridos = DFS(self)

        # Por cada recorrido.
        for recorrido in recorridos:
            # Obtenemos el nodo que retorna el recorrido.
            id_nodo = recorrido[-1]

            # Nodo actual
            nodo: Nodo_Binario = self[id_nodo]

            # Si el nodo es una hoja o un simbolo.
            if nodo.es_hoja():
                # Codigo del simbolo.
                codigo = ''

                # Por cada conexion en el recorrido y sus nodos
                i = 0
                for _ in recorrido[:-1]:
                    # Recupera el costo de moverse de i a i + 1.
                    costo = self[recorrido[i]].costo_hacia(
                        recorrido[i + 1]
                    )

                    # Concatenalo al codigo.
                    codigo += str(costo)
                    i += 1

                # Agrega el codigo a la tabla de codificacion.
                self.tabla_codificacion[
                    nodo.propiedades['simbolo']
                ] = codigo

    def codificar(self, texto: str) -> str:
        # Codifica un texto dado con el esquema.
        texto_codificado = ''

        for caracter in texto:
            codigo = self.tabla_codificacion[caracter]
            texto_codificado += codigo

        return texto_codificado

    def decodificar(self, texto_codificado: str) -> str:
        # Decodifica un texto codificado con el esquema.
        texto = ''

        # Puntero auxiliar.
        puntero = self.raiz

        # Por cada simbolo en el texto codificado.
        for simbolo_bit in texto_codificado:
            # Recuperamos el bit.
            bit = int(simbolo_bit)

            # Instanciamos el nodo del puntero.
            nodo: Nodo_Binario = self[puntero]

            # Instanciamos un puntero auxiliar.
            puntero_aux = None

            #  Si el bit es 1, nos movemos a la derecha, sino, nos
            # movemos a la izquierda.
            if bit == 1:
                puntero_aux = nodo.hijo_derecha

            else:
                puntero_aux = nodo.hijo_izquierda

            # Si el nodo hijo es una hoja, entonces retornamos el
            # simbolo decodificado y reseteamos el puntero a la raiz
            # del arbol.
            if self[puntero_aux].es_hoja():
                texto += self[puntero_aux].propiedades['simbolo']
                puntero = self.raiz

            # Sino, movemos el puntero.
            else:
                puntero = puntero_aux

        return texto

    def deltas_nodos(self) -> 'pd.Series':
        # Retorna una serie con los deltas de los nodos, o la diferencia
        # entre ramas de la frecuencia de los nodos.
        deltas = pd.Series(dtype=np.float64)

        # Por cada nodo en el arbol.
        for id_nodo in self:
            # Instanciamos el nodo.
            nodo: Nodo_Binario = self[id_nodo]

            # Si no es una hoja.
            if not nodo.es_hoja():
                # Se calcula el delta de las frecuencias de sus ramas.
                delta = (
                    self[nodo.hijo_derecha].propiedades['valor']
                    - self[nodo.hijo_izquierda].propiedades['valor']
                )

                # Unicamente deltas mayores a 0 son tomadas en cuenta.
                if delta > 0:
                    deltas[id_nodo] = delta

        return deltas

    def longitud_promedio_salida(self) -> float:
        Ls = 0

        # Por cada simbolo en el alfabeto.
        for simbolo in self.tabla_codificacion.index:
            # Buscamos su codigo.
            codigo = self.tabla_codificacion[simbolo]
            id = self.alfabeto[simbolo]

            # Calculamos la longitud promedio de salida,
            # longitud del codigo * frecuencia de simbolo.
            Ls += len(codigo) * self.frecuencias[id]

        # Las unidades son equivalentes al tipo de operacion.
        return Ls

    def radio_comprecion(self, Le: float) -> float:
        # Calcula el radio de comprecion del esquema.
        Ls = self.longitud_promedio_salida()

        return Le / Ls


class Arbol_Huffman_Modificado(Arbol_Huffman):

    def __init__(
        self,
        alfabeto: 'pd.DataFrame',
        frecuencias: 'pd.DataFrame'
    ) -> None:
        # Constructor de la clase padre.
        super().__init__(alfabeto, frecuencias)

        # Agregamos las modificaciones
        # necesarias para poder implementar
        # el algoritmo.
        self.alfabeto['ES'] = 'ES'
        self.alfabeto['Mx'] = 'Mx'

        self.frecuencias['ES'] = 0
        self.frecuencias['Mx'] = np.inf

        if len(self.frecuencias) > 0:
            mensaje = 'Se agregan los simbolos ES y Mx y'
            mensaje += ' sus frecuencias 0 e infinito.\n{}'
            self.log[self.contar.__next__()] = mensaje.format(
                self.frecuencias
            )

        # Tabla de codificacion izquierda.
        self.tabla_codificacion_izquierda = pd.Series(dtype=str)

        # Tabla de codificacion derecha.
        self.tabla_codificacion_derecha = pd.Series(dtype=str)

    def __construir_arbol_binario(
        self,
    ) -> None:
        '''
            Se contruye el arbol de huffman regular, sin aplicar
            las modificaciones.
        '''

        mensaje = 'Iniciamos la construcción del arbol binario'
        self.log[self.contar.__next__()] = mensaje

        # Limpiamos el arbol binario.
        self.flush()

        # Limpiamos la tabla de frecuencias sigma.
        self.frecuencias_sigma = pd.Series(dtype=np.float64)

        # Instanciamos un zip con el simbolo y el id del simbolo.
        simbolo_id = zip(
            self.alfabeto.index,
            self.alfabeto
        )

        mensaje = 'Agregamos los primeros nodos al arbol binario'
        mensaje += ', nodos agregados:\n'
        # Agregamos las hojas al arbol binario.
        for simbolo, id_hoja in simbolo_id:
            mensaje += '\t{}\n'.format(id_hoja)
            self[id_hoja] = Nodo_Binario(
                id_hoja,
                valor=self.frecuencias[id_hoja],
                simbolo=simbolo
            )

        self.log[self.contar.__next__()] = mensaje

        # Primero creamos una copia auxiliar de las frecuencias.
        frecuencias_aux = self.frecuencias.copy()

        # Organizamos las frecuencias de manera decendente.
        frecuencias_aux.sort_values(ascending=True, inplace=True)

        # Ahora construimos el arbol desde las hojas hasta la raiz.
        s = 0
        while not frecuencias_aux.empty:
            mensaje = 'Organizamos las frecuencias de manera ascendente\n'
            mensaje += frecuencias_aux.to_string()
            self.log[self.contar.__next__()] = mensaje

            # Extraemos los simbolos con menor frecuencia.
            simbolo_a = frecuencias_aux.index[0]
            simbolo_b = frecuencias_aux.index[1]

            mensaje = 'Se seleccionan los dos simbolos '
            mensaje += 'o sigmas con menor frecuencia '
            mensaje += '{} y {} son seleccionados'
            self.log[
                self.contar.__next__()
            ] = mensaje.format(simbolo_a, simbolo_b)

            # Calculamos su sigma, una suma de las frecuencias de ambos
            # simbolos.
            id_sigma = 'N{}'.format(s)
            sigma = frecuencias_aux[simbolo_a] + frecuencias_aux[simbolo_b]

            mensaje = 'Calculamos el sigma de {} y {} = {}'
            mensaje += ' y agregamos el nodo {} con el valor del sigma'
            self.log[self.contar.__next__()] = mensaje.format(
                simbolo_a,
                simbolo_b,
                sigma,
                id_sigma
            )

            # Se agrega el sigma a una tabla de frecuencias de sigma.
            self.frecuencias_sigma[id_sigma] = sigma
            self.frecuencias[id_sigma] = sigma

            # Se agrega el sigma como una frecuencia en la
            # tabla de frecuencias auxiliar.
            frecuencias_aux[id_sigma] = sigma

            # Agregamos el nodo del sigma con correspondencia a su
            # frecuencia calculada.
            if self.frecuencias[simbolo_a] > self.frecuencias[simbolo_b]:
                id_der = simbolo_a
                id_izq = simbolo_b

            else:
                id_der = simbolo_b
                id_izq = simbolo_a

            mensaje = 'El simbolo {} va a la derecha'
            mensaje += ' y el simbolo {} va a la izquierda de {}'
            self.log[self.contar.__next__()] = mensaje.format(
                id_der,
                id_izq,
                id_sigma
            )

            # Actualizamos la conexion del padre de los hijos del nodo
            # sigma.
            self[id_izq].padre = id_sigma
            self[id_der].padre = id_sigma

            # Agregamos el nodo sigma al arbol.
            self[id_sigma] = Nodo_Binario(
                id_sigma,
                hijo_izquierda=id_izq,
                hijo_derecha=id_der,
                valor=sigma
            )

            # Eliminamos las frecuencias seleccionadas de la tabla de
            # frecuencias auxiliar.
            frecuencias_aux.pop(simbolo_a)
            frecuencias_aux.pop(simbolo_b)

            # Si existe un unico elemento, eso quiere decir que
            # encontramos la raiz.
            if len(frecuencias_aux) <= 1:
                mensaje = 'Se termino de generar el'
                mensaje += ' arbol de huffman exitosamente'
                self.log[self.contar.__next__()] = mensaje

                break

            # Organizamos las frecuencias de manera decendente.
            frecuencias_aux.sort_values(ascending=True, inplace=True)

            # Aumentamos el conteo de sigmas.
            s += 1

        # El ultimo sigma calculado es la raiz del arbol.
        self.raiz = id_sigma

        mensaje = 'La raiz del arbol es el nodo {}'
        self.log[self.contar.__next__()] = mensaje.format(
            self.raiz
        )

        # Modificamos el arbol.
        self.__modificar_arbol()

        # self[self.raiz].propiedades['valor'] = sum(self.org_frecuencias)

        # Se cuentan el total de nodos en el arbol.
        self.total_nodos = len(self)

        # Restablecemos las frecuencias originales.
        self.frecuencias = self.org_frecuencias.copy()

    def __modificar_arbol(
        self,
    ) -> None:
        '''
            Realiza la modificación del arbol de huffman, produciendo
            MH.
        '''
        mensaje = 'Iniciamos la Modificación del arbol de huffman'
        self.log[self.contar.__next__()] = mensaje

        # Consultamos el id del hijo a la derecha de la raiz.
        id_aux = self[self.raiz].hijo_derecha

        # Topologia del sub arbol izquierda.
        sub_arbol = {}

        # Eliminamos el hijo derecho de la raiz.
        del self[id_aux]

        mensaje = 'Eliminamos el nodo {} del sub arbol derecho'
        self.log[self.contar.__next__()] = mensaje.format(id_aux)

        # Duplicamos el sub arbol izquierdo en el sub arbol derecho.
        for id_nodo in self:

            # Si el nodo no es la raiz.
            if id_nodo != self.raiz:
                # Se crea un id para el nodo que
                # corresponda al sub arbol derecho.
                id_l_nodo = 'R{}'.format(id_nodo)

                self.log[
                    self.contar.__next__()
                ] = 'Duplicando nodo {} en {}'.format(
                    id_nodo,
                    id_l_nodo
                )

                # El nodo es duplicado y se agrega al sub arbol derecho.
                sub_arbol[
                    id_l_nodo
                ] = copy.deepcopy(self[id_nodo])

                # Se asigna el id nuevo al nodo.
                sub_arbol[id_l_nodo].id_nodo = id_l_nodo

                # Si el nodo no es una hoja.
                if not sub_arbol[id_l_nodo].es_hoja():
                    # Se conecta el nodo con su hijo a la izquierda.
                    sub_arbol[id_l_nodo].hijo_izquierda = 'R{}'.format(
                        sub_arbol[id_l_nodo].hijo_izquierda
                    )

                    # Se conecta el nodo con su hijo a la derecha.
                    sub_arbol[id_l_nodo].hijo_derecha = 'R{}'.format(
                        sub_arbol[id_l_nodo].hijo_derecha
                    )

                # Si el padre del nodo es la raiz.
                if sub_arbol[id_l_nodo].padre == self.raiz:
                    # Se conecta la raiz con el nodo en el sub arbol
                    # derecho.
                    self[self.raiz].hijo_derecha = id_l_nodo

                # Si el nodo es hoja.
                else:
                    # El nodo padre se conecta con el nodo en el
                    # sub arbol derecho.
                    sub_arbol[id_l_nodo].padre = 'R{}'.format(
                        sub_arbol[id_l_nodo].padre
                    )

        mensaje = 'Se duplica el sub arbol izquierdo al'
        mensaje += ' sub arbol derecho, {} nodos duplicados'
        self.log[self.contar.__next__()] = mensaje.format(
            len(sub_arbol)
        )

        # Por cada nodo en el sub arbol derecho
        # se agrega al arbol.
        for id in sub_arbol:
            self[id] = sub_arbol[id]

        # Eliminamos el nodo ES en la derecha.
        self[self['RES'].padre].hijo_izquierda = None
        del self['RES']

        mensaje = 'Nodo RES del sub arbol derecho eliminado'
        self.log[self.contar.__next__()] = mensaje

    @time_it
    def generar_tabla_codigos(
        self,
    ) -> None:
        '''
            Se genera la tabla de codificacion del esquema.
        '''
        mensaje = 'Iniciamos la creación de las tablas de codificación'
        self.log[self.contar.__next__()] = mensaje

        # Generamos el arbol binario.
        self.__construir_arbol_binario()

        # indicamos el recorrido a usar para crear la tabla, en este 
        # se usara DFS.
        recorridos = DFS(self)

        mensaje = 'Se utilizara un recorrido primero por profundidad'
        mensaje += ' (DFS) para crear las tablas de codigos'
        self.log[self.contar.__next__()] = mensaje

        # Por cada recorrido.
        for recorrido in recorridos:
            # Obtenemos el ultimo nodo en el recorrido.
            id_nodo = recorrido[-1]

            # Nodo actual
            nodo: Nodo_Binario = self[id_nodo]

            mensaje = 'Recorrido terminado: {}'
            self.log[self.contar.__next__()] = mensaje.format(
                recorrido
            )

            # Si el nodo es una hoja o un simbolo.
            if nodo.es_hoja():
                mensaje = 'El nodo {} es hoja'
                self.log[self.contar.__next__()] = mensaje.format(
                    id_nodo
                )

                # Codigo del simbolo.
                codigo = ''

                # Index del codigo.
                i = 0

                # bit incial
                bit_inicial = self[recorrido[i]].costo_hacia(
                    recorrido[i + 1]
                )

                # Por cada conexion en el recorrido y sus nodos
                for _ in recorrido[:-1]:
                    # Recupera el costo de moverse de i a i + 1.
                    costo = self[recorrido[i]].costo_hacia(
                        recorrido[i + 1]
                    )

                    # Concatenalo al codigo.
                    codigo += str(costo)
                    i += 1

                mensaje = 'Código de {}: {}'
                self.log[self.contar.__next__()] = mensaje.format(
                    id_nodo,
                    codigo
                )

                mensaje = 'Nodo {} agregado en la tabla'
                if bit_inicial:
                    mensaje += ' derecha'
                    # Agrega el codigo a la tabla de codificacion.
                    self.tabla_codificacion_derecha[
                        nodo.propiedades['simbolo']
                    ] = codigo

                else:
                    mensaje += ' izquierda'
                    # Agrega el codigo a la tabla de codificacion.
                    self.tabla_codificacion_izquierda[
                        nodo.propiedades['simbolo']
                    ] = codigo

                self.log[self.contar.__next__()] = mensaje.format(
                    id_nodo
                )

        mensaje = 'Tabla de codificación derecha generada:\n{}'
        self.log[self.contar.__next__()] = mensaje.format(
            self.tabla_codificacion_derecha.to_string()
        )

        mensaje = 'Tabla de codificación izquerda generada:\n{}'
        self.log[self.contar.__next__()] = mensaje.format(
            self.tabla_codificacion_izquierda.to_string()
        )

    def reacomodar_secreto(
        self,
        secreto: 'str | bitarray.bitarray',
        semilla: int,
        binario: 'str | bitarray.bitarray',
        log: bool = True
    ) -> bitarray.bitarray:
        '''
            Reacomodamos el secreto.
        '''
        if log:
            mensaje = 'Iniciamos el reacomodo del binario'
            self.log[self.contar.__next__()] = mensaje

        # Establecemos la semilla para el generador
        # de numeros aleatorios.
        random.seed(semilla)

        if log:
            self.log[self.contar.__next__()] = 'La llave a usar es {}'.format(
                semilla
            )

        # Calculamos la longitud del binario.
        long_binario = len(binario)

        # Convertimos el tipo bitarray a string.
        if type(secreto) is bitarray.bitarray:
            secreto = secreto.to01()

        # Generamos un numero aleatorio con la misma cantidad de
        # bits que el binario.
        numero_mascara = random.getrandbits(long_binario)

        if log:
            mensaje = 'Mascara generada: {}'
            self.log[self.contar.__next__()] = mensaje.format(
                '{0:b}'.format(numero_mascara)
            )

            mensaje = 'Secreto pasado: {}'
            self.log[self.contar.__next__()] = mensaje.format(
                secreto
            )

        # De la mascara, restamos el valor del secreto decodificado
        # en decimal.
        numero_secreto = abs(numero_mascara - int(secreto, 2))

        # Convertimos el numero secreto a decimal.
        secreto_reacomodado = '{0:b}'.format(numero_secreto)

        # si la longitud del secreto reacomodado no coinicide con
        # la del secreto, se agregan 0 hasta que las
        # longitudes coincidan.
        while len(secreto_reacomodado) < long_binario:
            secreto_reacomodado = '0' + secreto_reacomodado

        if log:
            mensaje = 'Binario reacomodado: {}'
            self.log[self.contar.__next__()] = mensaje.format(
                secreto_reacomodado
            )

        return bitarray.bitarray(secreto_reacomodado)

    def reareglar_secreto(
        self,
        binario: 'str | bitarray.bitarray',
    ) -> bitarray.bitarray:
        # Convertimos el tipo bitarray a string.
        if type(binario) is bitarray.bitarray:
            binario = binario.to01()

        numero_mascara = -1
        numero_secreto = 1
        comparacion = 1
        while(
            numero_mascara < numero_secreto
            or comparacion != 0
        ):
            random.seed()
            semilla = random.randint(
                10,
                1e10
            )
            random.seed(semilla)
            numero_mascara = random.getrandbits(len(binario))
            numero_secreto = abs(numero_mascara - int(binario, 2))

            secreto = '{0:b}'.format(numero_secreto)

            while len(secreto) < len(binario):
                secreto = '0' + secreto

            binario_recuperado = self.reacomodar_secreto(
                secreto,
                semilla,
                binario,
                log=False
            )
            comparacion = int((bitarray.bitarray(binario) ^ binario_recuperado).to01(), 2)

        print('Llave generada: {}'.format(semilla))

        '''
            Rearegla el secreto.
        '''
        mensaje = 'Iniciamos el reareglo del binario'
        self.log[self.contar.__next__()] = mensaje

        # Establecemos la semilla para el generador
        # de numeros aleatorios.
        random.seed(semilla)

        self.log[self.contar.__next__()] = 'La llave a usar es {}'.format(
            semilla
        )

        # Generamos un numero aleatorio con la misma cantidad de
        # bits que el binario.
        numero_mascara = random.getrandbits(len(binario))

        mensaje = 'Mascara generada: {}'
        self.log[self.contar.__next__()] = mensaje.format(
            '{0:b}'.format(numero_mascara)
        )

        mensaje = 'El binario ingresado es {}'
        self.log[self.contar.__next__()] = mensaje.format(
            binario
        )

        # De la mascara, restamos el valor del secreto en decimal.
        numero_secreto = abs(numero_mascara - int(binario, 2))

        # Convertimos el numero secreto a binario.
        secreto = '{0:b}'.format(numero_secreto)

        # Si la longitud del secreto es mejor que la del binario
        # se agregan 0 a la izquerda hasta coincidir con la longitud
        # del binario.
        while len(secreto) < len(binario):
            secreto = '0' + secreto

        mensaje = 'Secreto generado: {}'
        self.log[self.contar.__next__()] = mensaje.format(
            secreto
        )

        return bitarray.bitarray(secreto), semilla

    @time_it
    def codificar(
        self,
        dir: 'str | pathlib.Path',
        archivo_salida: 'str | pathlib.Path',
        long_texto: int,
        binario: 'str | bitarray.bitarray',
        rescritura: bool,
        salida_datos: bool = True,
    ) -> 'tuple[str | bitarray.bitarray, int]':
        '''
            Codifica y embebe un mensaje secreto binario en la
            codificacion, es importante notar que
            len(texto) < len(secreto)
        '''
        mensaje = 'Iniciamos la codificación del medio'
        self.log[self.contar.__next__()] = mensaje

        # Verificamos que el binario sea menor que el texto.
        if len(binario) > long_texto:
            raise Exception('Código secreto mayor que el texto')

        mensaje = 'El binario es de menor '
        mensaje += 'longitud que el medio: {} <= {}'
        self.log[self.contar.__next__()] = mensaje.format(
            len(binario),
            long_texto
        )

        # Ahora reareglamos el binario.
        secreto, llave = self.reareglar_secreto(binario)

        # Mensaje codificado binario.
        stego = ''

        # Longitud del secreto.
        long_secreto = len(secreto)

        # Iterador del contenido del archivo.
        archivo = iterador_archivo(dir)

        mensaje = 'Medio {} cargado con exito,'
        mensaje += ' empezando con la codificación'
        self.log[self.contar.__next__()] = mensaje.format(
            pathlib.Path(dir).name
        )

        # Primero embebemos el secreto en la codificacion del cover.
        i = 0
        for i in range(long_secreto):
            # Obtenemos el bit en la posicion i del secreto
            bit = int(secreto[i])

            # Obtenemos el caracter en la posicion i del cover.
            caracter = archivo.__next__()

            # Codigo a agregar en el stego.
            codigo = ''

            # Si el bit es 1, entonces se codifica con el codigo a la
            # derecha.
            if bit == 1:
                codigo = self.tabla_codificacion_derecha[caracter]

            # Si es 0, se codifica con el codigo a la izquierda.
            else:
                codigo = self.tabla_codificacion_izquierda[caracter]

            mensaje = 'Embebiendo bit secreto {} en simbolo {}: {}'
            self.log[self.contar.__next__()] = mensaje.format(
                bit,
                caracter,
                codigo
            )

            # Agregamos el codigo al stego
            stego += codigo

        # Una vez terminada la integracion del secreto en el stego, se
        # agrega el codigo para ES.
        stego += self.tabla_codificacion_izquierda['ES']

        mensaje = 'Secreto embebido con exito, agregando ES: {}'
        mensaje += '\nTerminando de codificar el medio'
        self.log[self.contar.__next__()] = mensaje.format(
            self.tabla_codificacion_izquierda['ES']
        )

        # Ahora terminamos de codifiar el texto sobrante.
        for caracter in archivo:
            # Consultamos el codigo del caracter.
            codigo = self.tabla_codificacion_izquierda[caracter]

            mensaje = 'Codificando {}: {}'
            self.log[self.contar.__next__()] = mensaje.format(
                caracter,
                codigo
            )

            # Codigo a agregar en el stego.
            stego += codigo

        self.log[self.contar.__next__()] = 'Codificación finalizada'

        # Guardamos la codificación del texto en formato binario.
        buffer_stego = bitarray.bitarray(stego)

        # Verificamos si el stego es multiplo de 8.
        relleno = len(buffer_stego) % 8

        # Si es necesario rellenarlo.
        if relleno > 0:
            # Calculamos la cantidad de bits que el relleno del
            # stego debe tener para que sea multiplo de 8.
            relleno = 8 - relleno

            # Generamos combinaciones entre los bits de
            # la longitud del relleno.
            combinaciones = itertools.product([0, 1], repeat=relleno)
            bits_relleno = bitarray.bitarray(combinaciones.__next__())

            # Verificamos que el relleno no pueda ser decodificado.
            while len(self.__dec_relleno(bits_relleno)) > 0:
                bits_relleno = bitarray.bitarray(combinaciones.__next__())


        self.log[
            self.contar.__next__()
        ] = 'Codificación del stego {}'.format(
            buffer_stego.to01()
        )

        # Extendemos los bits del stego para que sea multiplo de 8.
        buffer_stego.extend(bits_relleno)

        if salida_datos:
            # Si la dirección al archivo es de tipo string, entonces se
            # convierte a un patlib object.
            if type(archivo_salida) == str:
                archivo_salida = pathlib.Path(archivo_salida)

            # Checamos si el archivo binario de salida existe.
            if archivo_salida.is_file() and not rescritura:
                raise Exception(
                    'El archivo {} ya existe'.format(archivo_salida.name)
                )

            with open(archivo_salida, 'wb+') as objeto_archivo:
                objeto_archivo.write(
                    buffer_stego.tobytes()
                )

            mensaje = 'Stego guardado en archivo {}'
            self.log[self.contar.__next__()] = mensaje.format(
                archivo_salida.name
            )


        return buffer_stego, llave

    def __dec_relleno(
        self,
        stego: 'str | bitarray.bitarray'
    ) -> 'tuple[str]':
        # Decodifica un texto codificado con el esquema.
        texto = ''

        # Resetamos el puntero a la raiz.
        puntero = self.raiz

        # Longitud del texto codificado.
        long_texto_cod = len(stego)

        # Por cada simbolo restante.
        i = 0
        while i < long_texto_cod:
            # Recuperamos el bit.
            bit = int(stego[i])

            # Recuperamos el nodo actual.
            nodo: Nodo_Binario = self[puntero]

            # Si el nodo es una hoja.
            if nodo.es_hoja():
                # Recuperamos el simbolo que represeta.
                simbolo = nodo.propiedades['simbolo']

                # Agregamos el simbolo decodificado al texto.
                texto += simbolo

                # Resetamos el puntero a la raiz.
                puntero = self.raiz

            # Si el nodo no es una hoja, nos seguimos moviendo.
            else:
                #  Si el bit es 1, nos movemos a la derecha, sino, nos
                # movemos a la izquierda.
                if bit == 1:
                    puntero = nodo.hijo_derecha

                else:
                    puntero = nodo.hijo_izquierda

                i += 1

        # Agregamos el ultimo simbolo, dado
        # al formato binario en el que se guarda el stego
        # en el archivo, es importante definir si es ultimo simbolo
        # es un simbolo valido o solo es de relleno.
        if self[puntero].es_hoja():
            # Si el simbolo es valido, se agrega al texto.
            simbolo = self[puntero].propiedades['simbolo']
            texto += simbolo

        return texto

    @time_it
    def decodificar(
        self,
        dir_archivo: 'str | pathlib.Path',
        archivo_salida: 'str | pathlib.Path',
        rescritura: bool,
        salida_datos: bool = True,
        stego: 'None | str |bitarray.bitarray' = None,
    ) -> 'tuple[str]':
        '''
            Decodifica un stego dado.
        '''
        mensaje = 'Iniciamos la decodificación del medio'
        self.log[self.contar.__next__()] = mensaje

        # Decodifica un texto codificado con el esquema.
        texto = ''

        # Secreto decodificado.
        secreto = ''

        # Puntero auxiliar.
        puntero = self.raiz

        if stego == None:
            # Si la dirección al archivo es de tipo string,
            # entonces se convierte a un patlib object.
            if type(dir_archivo) == str:
                dir_archivo = pathlib.Path(dir_archivo)

            # Si no es un archivo, entonces levanta una excepcion.
            if not dir_archivo.is_file():
                raise Exception('{} no es un archivo'.format(
                    dir_archivo.name
                ))

            # Verificamos que sea un archivo valido.
            if dir_archivo.suffix.lower() != '.bin':
                raise Exception('{} no es un archivo valido'.format(
                    dir_archivo.name
                ))

            mensaje = 'Cargamos el stego del archivo {}'
            self.log[self.contar.__next__()] = mensaje.format(
                dir_archivo.name
            )

            # Cargamos el contenido del archivo binario.
            stego = bitarray.bitarray()
            with open(dir_archivo, 'rb+') as objeto_archivo:
                stego.fromfile(objeto_archivo)

        else:
            mensaje = 'Estego pasado por parametros {}'
            self.log[self.contar.__next__()] = mensaje.format(
                stego.to01()
            )

            if type(stego) == str:
                stego = bitarray.bitarray(stego)

        # Longitud del texto codificado.
        long_texto_cod = len(stego)

        # Indica si se encontro el final del secreto.
        final_secreto = False

        mensaje = 'Empezamos la decodificación'
        mensaje += ' del stego con el secreto'
        self.log[self.contar.__next__()] = mensaje

        # Primero decodificamos el texto que contiene el secreto.
        i = 0
        primer_bit = int(stego[i])

        mensaje = 'Se agrego el bit {} al secreto recuperado'
        self.log[self.contar.__next__()] = mensaje.format(
            primer_bit
        )

        while not final_secreto and i < long_texto_cod:
            # Recuperamos el bit.
            bit = int(stego[i])

            # Recuperamos el nodo actual.
            nodo: Nodo_Binario = self[puntero]

            mensaje = 'El bit actual en el stego es {}'
            self.log[self.contar.__next__()] = mensaje.format(bit)

            # Si el nodo es una hoja.
            if nodo.es_hoja():
                # Recuperamos el simbolo que represeta.
                simbolo = nodo.propiedades['simbolo']

                # Si no es el simbolo de finalizacion del secreto
                # repetimos el proceso con el siguiente conjunt de bits
                if simbolo != 'ES':
                    # Resetamos puntero a la raiz
                    puntero = self.raiz

                    # Agregamos simbolo decodificado al texto
                    texto += simbolo

                    # Agregamos el primer bit al secret.
                    secreto += str(primer_bit)
 
                    # Actualizamos cual es el primer bit.
                    primer_bit = int(stego[i])

                    mensaje = 'Se agrego el bit secreto {}'
                    mensaje += ' al secreto recuperado {}'
                    mensaje += ' se decodifico el simbolo {}'
                    self.log[self.contar.__next__()] = mensaje.format(
                        primer_bit,
                        secreto,
                        simbolo
                    )

                # Si es el simbolo de finalizacion, terminamos el ciclo.
                else:
                    final_secreto = True

                    mensaje = 'Final del secreto encontrado'
                    mensaje += ' se decodifico el simbolo {}'
                    self.log[self.contar.__next__()] = mensaje.format(
                        simbolo
                    )

            # Si el nodo no es una hoja, nos seguimos moviendo.
            else:
                #  Si el bit es 1, nos movemos a la derecha, sino, nos
                # movemos a la izquierda.
                if bit == 1:
                    puntero = nodo.hijo_derecha

                else:
                    puntero = nodo.hijo_izquierda

                i += 1

        mensaje = 'Se termina de decodificar el stego'
        self.log[self.contar.__next__()] = mensaje

        # Resetamos el puntero a la raiz.
        puntero = self.raiz

        # Por cada simbolo restante.
        while i < long_texto_cod:
            # Recuperamos el bit.
            bit = int(stego[i])

            # Recuperamos el nodo actual.
            nodo: Nodo_Binario = self[puntero]

            mensaje = 'El bit en el stego actual es {}'
            self.log[self.contar.__next__()] = mensaje.format(bit)

            # Si el nodo es una hoja.
            if nodo.es_hoja():
                # Recuperamos el simbolo que represeta.
                simbolo = nodo.propiedades['simbolo']

                # Agregamos el simbolo decodificado al texto.
                texto += simbolo

                # Resetamos el puntero a la raiz.
                puntero = self.raiz

                mensaje = 'Se decodifico el simbolo {}'
                self.log[self.contar.__next__()] = mensaje.format(
                    simbolo
                )

            # Si el nodo no es una hoja, nos seguimos moviendo.
            else:
                #  Si el bit es 1, nos movemos a la derecha, sino, nos
                # movemos a la izquierda.
                if bit == 1:
                    puntero = nodo.hijo_derecha

                else:
                    puntero = nodo.hijo_izquierda

                i += 1

        # Agregamos el ultimo simbolo, dado
        # al formato binario en el que se guarda el stego
        # en el archivo, es importante definir si es ultimo simbolo
        # es un simbolo valido o solo es de relleno.
        if self[puntero].es_hoja():
            # Si el simbolo es valido, se agrega al texto.
            simbolo = self[puntero].propiedades['simbolo']

            texto += simbolo

            mensaje = 'Se decodifico el simbolo {}'
            self.log[self.contar.__next__()] = mensaje.format(
                simbolo
            )

        else:
            mensaje = 'Bits de relleno encontrados'
            self.log[self.contar.__next__()] = mensaje

        # Guardamos el texto decodificado.
        if salida_datos:
            # Si la dirección al archivo es de tipo string, entonces se
            # convierte a un patlib object.
            if type(archivo_salida) == str:
                archivo_salida = pathlib.Path(archivo_salida)

            # Checamos si el archivo binario de salida existe.
            if archivo_salida.is_file() and not rescritura:
                raise Exception(
                    'El archivo {} ya existe'.format(archivo_salida.name)
                )

            with open(archivo_salida, 'w+', encoding='utf-8') as objeto_archivo:
                objeto_archivo.write(texto)

            mensaje = 'Stego decodificado en {}'
            self.log[self.contar.__next__()] = mensaje.format(
                archivo_salida.name
            )

        return texto, secreto

    def cargar_datos(
        self,
        dir_archivo: 'str | pathlib.Path',
    ) -> None:
        '''
            Carga los datos del esquema desde un archivo
            serializado con pickle.
        '''

        mensaje = 'Iniciamos el cargado del esquema'
        self.log[self.contar.__next__()] = mensaje

        # Si el directorio pasado no es de tipo
        # Path, se pasa a ese formato.
        if type(dir_archivo) == str:
            dir_archivo = pathlib.Path(dir_archivo)

        # Verificamos que sea un archivo y que exista.
        if not dir_archivo.is_file():
            raise Exception('No es archivo')

        with open(dir_archivo, 'rb+') as objeto_archivo:
            mensaje = 'Cargamos el archivo {}'
            self.log[self.contar.__next__()] = mensaje.format(
                dir_archivo.name
            )

            datos = pickle.load(objeto_archivo)

            self.flush()
            self.total_nodos = len(datos['arbol_binario'])

            self.raiz = datos['raiz']
            self.alfabeto = datos['alfabeto']
            self.frecuencias = datos['frecuencias']
            self.tabla_codificacion_derecha = datos[
                'tabla_codificacion_derecha'
            ]
            self.tabla_codificacion_izquierda = datos[
                'tabla_codificacion_izquierda'
            ]

            self.log[
                self.contar.__next__()
            ] = 'Frecuencias cargadas\n{}'.format(
                self.frecuencias.to_string()
            )

            self.log[
                self.contar.__next__()
            ] = 'Alfabeto cargadas\n{}'.format(
                self.alfabeto.to_string()
            )

            self.log[
                self.contar.__next__()
            ] = 'Tabla de codificación izquerda cargada\n{}'.format(
                self.tabla_codificacion_izquierda.to_string()
            )

            self.log[
                self.contar.__next__()
            ] = 'Tabla de codificación derecha cargada\n{}'.format(
                self.tabla_codificacion_derecha.to_string()
            )

            self.log[
                self.contar.__next__()
            ] = 'Cargando árbol binario'

            for id_nodo in datos['arbol_binario']:
                nodo = datos['arbol_binario'][id_nodo]
                self[id_nodo] = nodo

                self.log[
                    self.contar.__next__()
                ] = 'Nodo {} cargado en árbol binario'.format(
                    nodo.id_nodo
                )

    def serizalizar_datos(
        self,
        dir_archivo: 'str | pathlib.Path',
        rescritura: bool
    ) -> None:
        '''
            Serializa los datos a un archivo binario con pickle.
        '''

        mensaje = 'Iniciamos el guardado del esquema'
        self.log[self.contar.__next__()] = mensaje

        # Si el directorio pasado no es de tipo
        # Path, se pasa a ese formato.
        if type(dir_archivo) == str:
            dir_archivo = pathlib.Path(dir_archivo)

        # Verificamos que el archivo no exista.
        if dir_archivo.is_file() and not rescritura:
            raise Exception(
                'El archivo {} ya existe'.format(dir_archivo.name)
            )

        topologia = {}
        # Copiamos la topologia del arbol binario.
        for id_nodo in self:
            topologia[id_nodo] = self[id_nodo]

        with open(dir_archivo, 'wb+') as objeto_archivo:
            # Datos que se seralizaran.
            datos = {
                'tabla_codificacion_izquierda': self.tabla_codificacion_izquierda,
                'tabla_codificacion_derecha': self.tabla_codificacion_derecha,
                'alfabeto': self.alfabeto,
                'frecuencias': self.org_frecuencias,
                'arbol_binario': topologia,
                'raiz': self.raiz
            }

            # Serializamos los datso en el archivo.
            pickle.dump(datos, objeto_archivo)

        mensaje = 'Guardamos el esquema en el archivo {}'
        self.log[self.contar.__next__()] = mensaje.format(
            dir_archivo.name
        )