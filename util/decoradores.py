# Librerias estandar.
import time


def time_it(func):
    '''
        Decorador que calcula el tiempo
        de ejecución de la función.
    '''

    def wrapper(*args,**kwargs):
        a = time.time()
        resultado = func(*args, **kwargs)
        b = time.time()
        print('Función {} ejectutada en {}s'.format(func.__name__, round(b - a, 4)))
        return resultado
        
    return wrapper