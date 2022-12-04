'''
    Codificación de alfabetos, se utilizan distintos metodos
    para codificar alfabetos.
'''


# !/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Librerias estandar.
import os
import random
import pathlib
import platform
import argparse
import filecmp

# Librerias de terceros.
import bitarray
import pandas as pd

# Librerias propias.
from util.constantes import FORMATOS_VALIDOS
from util.graficador import graficar_arbol_binario
from esquema.huffman import Arbol_Huffman_Modificado, Arbol_Huffman
from util.archivos import analizar_archivo, nombre_generico


def argumentos_consola(
) -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        description='''
            PIA de Teoría de la información y
            métodos de codificación
        '''
    )

    arg_parser.add_argument(
        '--codifica',
        default=None,
        help='''
            Directorio de un archivo, indica al
            programa que se desea codificar el
            archivo, los formatos de archivos
            soportados on .pdf y .txt
        ''',
        dest='dir_archivo_cod',
        type=str,
    )

    arg_parser.add_argument(
        '--decodifica',
        default=None,
        help='''
            Directorio de un archivo, indica al
            programa que se desea decodificar el archivo
        ''',
        dest='dir_archivo_decod',
        type=str,
    )

    arg_parser.add_argument(
        '--esquema',
        default=None,
        help='''
            Dirección del archivo del esquema a usar,
            obligatorio si se desea descomprimir un archivo
        ''',
        dest='dir_archivo_esquema',
        type=str,
    )

    arg_parser.add_argument(
        '--llave',
        default=None,
        help='Llave usada para el reacomodo del binario',
        dest='semilla',
        type=int
    )

    arg_parser.add_argument(
        '--binario',
        default=None,
        help='''
            Binario que se utiliza para
            embeber en el texto
        ''',
        dest='binario',
        type=str
    )

    arg_parser.add_argument(
        '--pruebas',
        default=None,
        help='''
            Directorio donde se encuentran archivos
            para realizar pruebas al algoritmo
        ''',
        dest='benchmark',
        type=str
    )

    arg_parser.add_argument(
        '-o',
        default=None,
        help='''
            Indica si se crearan los archivos
            de salida del programa
        ''',
        dest='salidas',
        type=str
    )

    arg_parser.add_argument(
        '-r',
        default=None,
        help='''
            Indica si los archivos de salida se
            reescriben, por default es falso
        ''',
        dest='rescritura',
        type=str
    )

    arg_parser.add_argument(
        '-g',
        default=None,
        help='''
            Indica si se crea el grafico del esquema.
        ''',
        dest='grafico',
        type=str
    )

    arg_parser.add_argument(
        '-l',
        default=None,
        help='''
            Indica si las acciones y operaciones
            que el programa realiza seran guardadas en un archivo log.
        ''',
        dest='log',
        type=str
    )

    args = arg_parser.parse_args()

    return args


def pruebas(
    dir_archivos: str,
    rescritura: bool,
    grafico: bool,
    log: bool,
    dir_binario: 'str | None'
) -> None:
    # Directorio donde se encuentran los archivos de prueba.
    dir_archivos = pathlib.Path(dir_archivos)

    # Delcaramos el binario.
    binario = None

    # Si el directorio no existe, entonces se levanta
    # una excepción.
    if not dir_archivos.is_dir() and not dir_archivos.is_file():
        raise Exception('El directorio o archivo no existe')

    if dir_binario != None:
        # Se paso un archivo de texto plano para
        # embeber como secreto en los archivos de prueba.
        dir_binario = pathlib.Path(dir_binario)

        # Verificamos que el binario sea un archivo de formato valido.
        if not dir_binario.is_file():
            raise Exception('El binario debe de ser un archivo')

        if dir_binario.suffix.lower() not in FORMATOS_VALIDOS:
            raise Exception('el formato del archivo binario no es valido')

        # Realizamos el análisis estadistico del árbol de huffman.
        frec_bin, alf_bin = analizar_archivo(dir_binario)

        # Creamos un esquema para el documento que se guardara como el secreto.
        esquema_secreto = Arbol_Huffman(alf_bin, frec_bin)

        # Generamos la tabla de codificación del esquema del binario.
        esquema_secreto.generar_tabla_codigos()

        # Codificamos el binario.
        binario = esquema_secreto.codificar(medio=dir_binario)

        # Generamos el grafico del esquema.
        if grafico:
            graficar_arbol_binario(
                esquema_secreto,
                dir_binario.name.split('.')[0]
            )

            esquema_secreto.log[
                esquema_secreto.contar.__next__()
            ] = 'Grafico de árbol de huffman guardado en {}'.format(
                dir_binario.name.split('.')[0] + '.svg'
            )

        if log:
            with open(
                dir_binario.name.split('.')[0] + '.log',
                'w+',
                encoding='UTF-8'
            ) as archivo_log:
                for id_log in esquema_secreto.log:
                    archivo_log.write(
                        '[LOG: {}]: {}\n'.format(
                            id_log,
                            esquema_secreto.log[id_log]
                        )
                    )

    total_archivos = 0
    resultados = {
        'Peso archivo (bits)': [],
        'Código Huffman (bits)': [],
        'Cantidad Simbolos': [],
        'Bits Secretos (bits)': [],
        'Stego (bits)': [],
        'Memoria salvada (%)': []
    }

    if dir_archivos.is_file():
        fichero = dir_archivos

        print('\nArchivo {} : Medio {}'.format(
            fichero.name,
            total_archivos + 1
        ))
        print('-'*50)

        for metrica in list(resultados.keys()):
            resultados[metrica].append(0)

        # Consultamos el peso del archivo.
        resultados[
            'Peso archivo (bits)'
        ][total_archivos] = fichero.stat().st_size * 8

        # Calculamos las frecuencias y el alfabeto.
        frecuencias, alfabeto = analizar_archivo(fichero)

        # Calculamos la longitud del texto.
        longitud_texto = sum(frecuencias)
        resultados[
            'Cantidad Simbolos'
        ][total_archivos] = longitud_texto

        # Generamos un secreto que abarque
        # todos los espacios disponibles.
        if binario is None:
            binario = bitarray.bitarray(longitud_texto)

        # Calculamos la longitud del secreto.
        longitud_binario = len(binario)
        resultados[
            'Bits Secretos (bits)'
        ][total_archivos] = longitud_binario

        # Instanciamos el esquema del arbol
        # de huffman modificado.
        huffman_mod = Arbol_Huffman_Modificado(
            alfabeto,
            frecuencias
        )

        # Generamos las tablas de codigos del
        # arbol de huffman modificado.
        huffman_mod.generar_tabla_codigos()

        # Codificamos el texto.
        stego, llave = huffman_mod.codificar(
            fichero,
            None,
            longitud_texto,
            binario,
            rescritura,
            salida_datos=False
        )

        # Nombre del archivo con la codificación.
        archivo_decod = nombre_generico(
            fichero.name.split('.')[0]
        )

        texto_deco, secreto = huffman_mod.decodificar(
            None,
            archivo_decod + '.txt',
            False,
            True,
            stego
        )

        archivo_decod = pathlib.Path(
            archivo_decod + '.txt'
        )

        comparacion = filecmp.cmp(
            archivo_decod,
            fichero,
            shallow=False
        )

        if comparacion:
            mensaje = 'El archivo original {} es '
            mensaje += 'similar al archivo {} decodificado'
            print(mensaje.format(fichero.name, archivo_decod.name))

        else:
            mensaje = 'El archivo original {} es '
            mensaje += 'diferente al archivo {} decodificado'
            print(mensaje.format(fichero.name, archivo_decod.name))

        binario_recuperado = huffman_mod.reacomodar_secreto(
            secreto,
            llave,
            binario.to01()
        )
        comparacion = binario ^ binario_recuperado

        mensaje = 'Binario comparado con el secreto recuperado: {}'
        huffman_mod.log[huffman_mod.contar.__next__()] = mensaje.format(
            comparacion.to01()
        )

        if int(comparacion.to01(), 2) == 0:
            print('Binario recuperado correctamente')

            if dir_binario is not None:

                # Decodificamos el binario secreto recuperado
                # con el esquema para el binario.
                texto_secreto = esquema_secreto.decodificar(
                    binario_recuperado
                )

                # Creamos un nombre para el archivo del texto secreto recuperado.
                dir_binario_recuperado = dir_binario.name.split('.')[0]
                dir_binario_recuperado +=  '_recuperado_secreto.txt'
                dir_binario_recuperado = pathlib.Path(dir_binario_recuperado)

                # Creamos el archivo con el texto del secreto.
                with open(dir_binario_recuperado, 'w+', encoding='utf-8') as bin_rec:
                    bin_rec.write(texto_secreto)

                # Comparamos el contenido del archivo
                # seleccionado como el binario y el texto secreto recuperado.
                comparacion = filecmp.cmp(
                    dir_binario,
                    dir_binario_recuperado,
                    shallow=False
                )

                # Mostramos la comparación
                if comparacion:
                    mensaje = 'El archivo seleccionado como binario {} es '
                    mensaje += 'similar al texto secreto {} recuperado'
                    print(mensaje.format(
                        dir_binario.name,
                        dir_binario_recuperado.name
                    ))

        # Calculamos la longitud del stego.
        longitud_stego = len(stego)
        resultados['Stego (bits)'][total_archivos] = longitud_stego

        # Calculamos la longitud de la codificacion de huffman.
        longitud_huffman = longitud_stego - longitud_binario - len(
            huffman_mod.tabla_codificacion_izquierda['ES']
        )
        resultados[
            'Código Huffman (bits)'
        ][total_archivos] = longitud_huffman

        resultados[
            'Memoria salvada (%)'
        ][total_archivos] = round(
            1 - (longitud_stego / (fichero.stat().st_size * 8)),
            2
        ) * 100

        # Generamos el grafico del esquema.
        if grafico:
            graficar_arbol_binario(
                huffman_mod,
                fichero.name.split('.')[0]
            )

            graficar_arbol_binario(
                huffman_mod.huffman_normal,
                fichero.name.split('.')[0] + '_normal'
            )

            huffman_mod.log[
                huffman_mod.contar.__next__()
            ] = 'Grafico de árbol de huffman guardado en {}'.format(
                fichero.name.split('.')[0] + '.svg'
            )

        if log:
            with open(
                fichero.name.split('.')[0] + '.log',
                'w+',
                encoding='UTF-8'
            ) as archivo_log:
                for id_log in huffman_mod.log:
                    archivo_log.write(
                        '[LOG: {}]: {}\n'.format(
                            id_log,
                            huffman_mod.log[id_log]
                        )
                    )

        total_archivos += 1

    else:
        binario_recuperado_completo = {}

        ficheros = {
        }

        a = 0
        b = 0
        a_aux = 0

        total_ficheros = 0
        for fichero in dir_archivos.iterdir():
            # Calculamos las frecuencias y el alfabeto del fichero.
            frecuencias, alfabeto = analizar_archivo(fichero)

            longitud_texto = sum(frecuencias)

            if dir_binario is not None:
                if a > -1:
                    # Si se paso un archivo para ser parte del binario,
                    # el binario es seccionado para que pueda ser 
                    # embebido en la mayoria o todos los archivos.
                    b = a + longitud_texto if a + longitud_texto < len(binario) else -1
                    if b == -1:
                        binario_asignado = binario[
                            a:
                        ]
                    else:
                        binario_asignado = binario[
                            a:b
                        ]
                    a_aux = a
                    a = b
                else:
                    binario_asignado = bitarray.bitarray()

            else:
                # Generamos un secreto que abarque
                # todos los espacios disponibles.
                binario_asignado = bitarray.bitarray(longitud_texto)

            # Asignamos los datos del fichero.
            datos_fichero = {
                'frecuencias': frecuencias,
                'alfabeto': alfabeto,
                'capacidad': longitud_texto,
                'binario': binario_asignado,
                'seccion': (a_aux, b)
            }

            ficheros[fichero.name] = datos_fichero

            total_ficheros += 1

        print('Cargando {} archivos'.format(total_ficheros))

        # Listamos todos los arhicvos del directorio.
        for fichero in dir_archivos.iterdir():
            if(
                fichero.is_file() and fichero.suffix.lower() in FORMATOS_VALIDOS
            ):
                print('\nArchivo {} : Medio {}'.format(
                    fichero.name,
                    total_archivos + 1
                ))
                print('-'*50)

                for metrica in list(resultados.keys()):
                    resultados[metrica].append(0)

                # Consultamos el peso del archivo.
                resultados[
                    'Peso archivo (bits)'
                ][total_archivos] = fichero.stat().st_size * 8

                datos_fichero = ficheros[fichero.name]

                # Calculamos las frecuencias y el alfabeto.
                frecuencias = datos_fichero['frecuencias']
                alfabeto = datos_fichero['alfabeto']

                # Calculamos la longitud del texto.
                longitud_texto = datos_fichero['capacidad']

                # Generamos un secreto que abarque
                # todos los espacios disponibles.
                binario_seleccionado = datos_fichero['binario']

                resultados[
                    'Cantidad Simbolos'
                ][total_archivos] = longitud_texto

                # Calculamos la longitud del secreto.
                longitud_binario = len(binario_seleccionado)
                resultados[
                    'Bits Secretos (bits)'
                ][total_archivos] = longitud_binario

                # Instanciamos el esquema del arbol
                # de huffman modificado.
                huffman_mod = Arbol_Huffman_Modificado(
                    alfabeto,
                    frecuencias
                )

                # Generamos las tablas de codigos del
                # arbol de huffman modificado.
                huffman_mod.generar_tabla_codigos()

                # Codificamos el texto.
                stego, llave = huffman_mod.codificar(
                    fichero,
                    None,
                    longitud_texto,
                    binario_seleccionado,
                    rescritura,
                    salida_datos=False
                )

                # Nombre del archivo con la codificación.
                archivo_decod = nombre_generico(
                    fichero.name.split('.')[0]
                )

                texto_deco, secreto = huffman_mod.decodificar(
                    None,
                    archivo_decod + '.txt',
                    False,
                    True,
                    stego
                )

                archivo_decod = pathlib.Path(
                    archivo_decod + '.txt'
                )

                comparacion = filecmp.cmp(
                    archivo_decod,
                    fichero,
                    shallow=False
                )

                if comparacion:
                    mensaje = 'El archivo original {} es '
                    mensaje += 'similar al archivo {} decodificado'
                    print(mensaje.format(fichero.name, archivo_decod.name))

                else:
                    mensaje = 'El archivo original {} es '
                    mensaje += 'diferente al archivo {} decodificado'
                    print(mensaje.format(fichero.name, archivo_decod.name))

                binario_recuperado = huffman_mod.reacomodar_secreto(
                    secreto,
                    llave,
                    binario_seleccionado.to01()
                )
                comparacion = binario_seleccionado ^ binario_recuperado

                if dir_binario is not None:
                    binario_recuperado_completo[fichero.name] = binario_recuperado

                mensaje = 'Binario comparado con el secreto recuperado: {}'
                huffman_mod.log[huffman_mod.contar.__next__()] = mensaje.format(
                    comparacion.to01()
                )

                if int(comparacion.to01(), 2) == 0:
                    print('Binario recuperado correctamente')

                # Calculamos la longitud del stego.
                longitud_stego = len(stego)
                resultados['Stego (bits)'][total_archivos] = longitud_stego

                # Calculamos la longitud de la codificacion de huffman.
                longitud_huffman = longitud_stego - longitud_binario - len(
                    huffman_mod.tabla_codificacion_izquierda['ES']
                )
                resultados[
                    'Código Huffman (bits)'
                ][total_archivos] = longitud_huffman

                resultados[
                    'Memoria salvada (%)'
                ][total_archivos] = round(
                    1 - (longitud_stego / (fichero.stat().st_size * 8)),
                    2
                ) * 100

                # Generamos el grafico del esquema.
                if grafico:
                    graficar_arbol_binario(
                        huffman_mod,
                        fichero.name.split('.')[0]
                    )

                    graficar_arbol_binario(
                        huffman_mod.huffman_normal,
                        fichero.name.split('.')[0] + '_normal'
                    )

                    huffman_mod.log[
                        huffman_mod.contar.__next__()
                    ] = 'Grafico de árbol de huffman guardado en {}'.format(
                        fichero.name.split('.')[0] + '.svg'
                    )

                if log:
                    with open(
                        fichero.name.split('.')[0] + '.log',
                        'w+',
                        encoding='UTF-8'
                    ) as archivo_log:
                        for id_log in huffman_mod.log:
                            archivo_log.write(
                                '[LOG: {}]: {}\n'.format(
                                    id_log,
                                    huffman_mod.log[id_log]
                                )
                            )

                total_archivos += 1

    dataset = pd.DataFrame(
        resultados, index=[
            'Medio {}'.format(i + 1) for i in range(total_archivos)
    ])

    if dir_binario is not None:
        binario_completo_recuperado = bitarray.bitarray(''.join(
            [bin.to01() for bin in binario_recuperado_completo.values()]
        ))

        if int((binario_completo_recuperado ^ binario).to01(), 2) == 0:
            print('Binario recuperado correctamente')

            texto_secreto = esquema_secreto.decodificar(
                binario_completo_recuperado
            )

            # Creamos un nombre para el archivo del texto secreto recuperado.
            dir_binario_recuperado = dir_binario.name.split('.')[0]
            dir_binario_recuperado +=  '_recuperado_secreto.txt'
            dir_binario_recuperado = pathlib.Path(dir_binario_recuperado)

            # Creamos el archivo con el texto del secreto.
            with open(dir_binario_recuperado, 'w+', encoding='utf-8') as bin_rec:
                bin_rec.write(texto_secreto)

            # Comparamos el contenido del archivo
            # seleccionado como el binario y el texto secreto recuperado.
            comparacion = filecmp.cmp(
                dir_binario,
                dir_binario_recuperado,
                shallow=False
            )

            # Mostramos la comparación
            if comparacion:
                mensaje = 'El archivo seleccionado como binario {} es '
                mensaje += 'similar al texto secreto {} recuperado'
                print(mensaje.format(
                    dir_binario.name,
                    dir_binario_recuperado.name
                ))


    print('-'*50)
    print(dataset.to_string())


def codificar(
    archivo: str,
    binario: str,
    rescritura: bool,
    grafico: bool,
    salidas: bool,
    log: bool,
) -> None:
    '''
        Codifica el archivo dado y embebe el
        binario reareglado por la semilla.
    '''

    # Analisamos las frecuencias y el alfabeto del archivo.
    frecuencias, alfabeto = analizar_archivo(archivo)

    # Longitud del texto.
    longitud_texto = sum(frecuencias)

    # Instanciamos el esquema del arbol
    # de huffman modificado.
    huffman_mod = Arbol_Huffman_Modificado(alfabeto, frecuencias)

    # Generamos las tablas de codigos del arbol de huffman modificado.
    huffman_mod.generar_tabla_codigos()

    # Nombre del archivo con la codificación.
    archivo_cod = nombre_generico(
        pathlib.Path(archivo).name.split('.')[0]
    )

    # Codificamos el texto.
    stego = huffman_mod.codificar(
        archivo,
        archivo_cod + '.bin',
        longitud_texto,
        binario,
        rescritura,
        salidas,
    )

    if salidas:
        # Serializamos el esquema del arbol de huffman modificado.
        huffman_mod.serizalizar_datos(
            archivo_cod  + '.huf',
            rescritura
        )

    # Generamos el grafico del esquema.
    if grafico:
        graficar_arbol_binario(
            huffman_mod,
            archivo_cod
        )

        graficar_arbol_binario(
            huffman_mod.huffman_normal,
            archivo_cod + '_normal'
        )

        huffman_mod.log[
            huffman_mod.contar.__next__()
        ] = 'Grafico de árbol de huffman guardado en {}'.format(
            archivo_cod + '.svg'
        )

    if log:
        with open(
            archivo_cod + '.log',
            'w+',
            encoding='UTF-8'
        ) as archivo_log:
            for id_log in huffman_mod.log:
                archivo_log.write(
                    '[LOG: {}]: {}\n'.format(
                        id_log,
                        huffman_mod.log[id_log]
                    )
                )


def decodificar(
    archivo: str,
    esquema: str,
    semilla: int,
    binario: str,
    rescritura: bool,
    grafico: bool,
    salidas: bool,
    log: bool,
) -> None:
    '''
        Decodifica el archivo
        binario con un esquema dado.
    '''
    # Instanciamos el esquema del arbol
    # de huffman modificado.
    huffman_mod = Arbol_Huffman_Modificado(pd.DataFrame(), pd.DataFrame())

    # Cargamos el esquema.
    huffman_mod.cargar_datos(
        esquema,
    )

    # Nombre del archivo con la codificación.
    archivo_decod = nombre_generico(
        pathlib.Path(archivo).name.split('.')[0]
    )

    # Decodifica el binario con el equema.
    texto, secreto = huffman_mod.decodificar(
        archivo,
        archivo_decod + '.txt',
        rescritura,
        salidas,
    )

    # Si recivimos la llave, reacomoda el secreto.
    if(semilla is not None):
        # Se verificia la legitimidad del usuario.
        binario_recuperado = huffman_mod.reacomodar_secreto(
            secreto,
            semilla,
            secreto if binario is None else binario,
        )

        # Si se pasa el binario, entonces se valida
        # con el binario recuperado.
        if binario is not None:
            binario = bitarray.bitarray(binario)

            comparacion = binario ^ binario_recuperado

            mensaje = 'Binario comparado con el secreto recuperado: {}'
            huffman_mod.log[huffman_mod.contar.__next__()] = mensaje.format(
                comparacion.to01()
            )

            if int(comparacion.to01(), 2) == 0:
                print('Binario validado exitosamente!')

    # Generamos el grafico del esquema.
    if grafico:
        graficar_arbol_binario(
            huffman_mod,
            archivo_decod
        )

        graficar_arbol_binario(
            huffman_mod.huffman_normal,
            archivo_decod + '_normal'
        )

    if log:
        with open(
            archivo_decod + '.log',
            'w+',
            encoding='UTF-8'
        ) as archivo_log:
            for id_log in huffman_mod.log:
                archivo_log.write(
                    '[LOG: {}]: {}\n'.format(
                        id_log,
                        huffman_mod.log[id_log]
                    )
                )


# Funcion main.
def main(
    con_args: argparse.Namespace,
    *args,
    **kwargs
) -> None:
    # Recuperamos los parametros pasados por consola.
    dir_archivo_cod: str = con_args.dir_archivo_cod
    dir_archivo_decod: str = con_args.dir_archivo_decod
    dir_archivo_esquema: str = con_args.dir_archivo_esquema
    semilla: int = con_args.semilla
    binario: str = con_args.binario
    benchmark: str = con_args.benchmark

    rescritura: str = con_args.rescritura
    grafico: str = con_args.grafico
    salidas: str = con_args.salidas
    log: str = con_args.log

    if rescritura is None:
        rescritura = False

    else:
        if rescritura.lower() == 't' or rescritura.lower() == '1':
            rescritura = True

        else:
            rescritura = False

    if grafico is None:
        grafico = False

    else:
        if grafico.lower() == 't' or grafico.lower() == '1':
            grafico = True

        else:
            grafico = False

    if salidas is None:
        salidas = True

    else:
        if salidas.lower() == 't' or salidas.lower() == '1':
            salidas = True

        else:
            salidas = False

    if log is None:
        log = False

    else:
        if log.lower() == 't' or log.lower() == '1':
            log = True

        else:
            log = False

    # Verificamos que tipo de operación desea realizar el usuario.
    if benchmark is not None:
        # El usuario desea ejecutar las pruebas del algoritmo.
        pruebas(
            benchmark,
            rescritura,
            grafico,
            log,
            binario
        )

    elif dir_archivo_cod is not None:
        if binario is None:
            raise Exception('''
                Es necesario pasar un binario,
                ingresa --h para más información
            ''')

        # El usuario busca comprimir un archivo.
        codificar(
            dir_archivo_cod,
            binario,
            rescritura,
            grafico,
            salidas,
            log,
        )

    elif dir_archivo_decod is not None:
        # El usuario busca descomprimir un archivo.
        if dir_archivo_esquema is None:
            raise Exception('''
                Es necesario pasar un esquema, ingresa --h para más información
            ''')

        arch_deco = pathlib.Path(dir_archivo_decod)
        if arch_deco.suffix.lower() != '.bin':
            raise Exception('Formato de {} no valido, formatos validos .bin'.format(arch_deco.name))
        
        arch_esquema = pathlib.Path(dir_archivo_esquema)
        if arch_esquema.suffix.lower() != '.huf':
            raise Exception('Formato de {} no valido, formatos validos .huf'.format(arch_esquema.name))

        decodificar(
            dir_archivo_decod,
            dir_archivo_esquema,
            semilla,
            binario,
            rescritura,
            grafico,
            salidas,
            log
        )


if __name__ == "__main__":
    con_args = argumentos_consola()
    if(
        con_args.dir_archivo_cod is None
        and con_args.dir_archivo_decod is None
        and con_args.benchmark is None
    ):
        print('Se debe seleccionar una acción a realizar, ingresa --h para más información')

    else:
        os.system(
            'cls' if platform.platform().split('-')[0] == 'Windows' else 'clear'
        )

        main(con_args)
        '''
        try:
        except Exception as error:
            print('Ocurrio un error: {}'.format(error))
        '''
