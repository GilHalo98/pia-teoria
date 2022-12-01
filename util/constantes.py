'''
    Enumeraciones de constantes.
'''


# !/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Librerias estandar.
from enum import Enum, auto


# Autoenumeracion de constantes.
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


# Tipos de operaciones.
class Tipo_Operacion(AutoName):
    CUANTIFICABLE = auto()
    TRANSMISION_DATOS = auto()
    TRANSICION_ESTADOS = auto()


# Formatos de archivos validos.
FORMATOS_VALIDOS = [
    '.pdf',
    '.txt'
]


# Simbolos especiales, aquellos que pueden
# o interfieren con Graphviz.
SIMBOLOS_ESPECIALES = {
    '{',
    '}',
    '<',
    '>'
}