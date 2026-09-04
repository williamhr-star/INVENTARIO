"""
Modelos de datos
"""
from .producto import Producto
from .venta import Venta
from .asiento import Asiento
from .parametro import Parametro

__all__ = [
    'Producto',
    'Venta',
    'Asiento',
    'Parametro'
]