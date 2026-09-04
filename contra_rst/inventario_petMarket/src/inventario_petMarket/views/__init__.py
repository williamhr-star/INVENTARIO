"""
Vistas de la aplicación
"""
from .dashboard import DashboardView
from .inventario import InventarioView
from .ventas import VentasView
from .contabilidad import ContabilidadView
from .asientos import AsientosView
from .reportes import ReportesView
from .configuracion import ConfiguracionView

__all__ = [
    'DashboardView',
    'InventarioView',
    'VentasView',
    'ContabilidadView',
    'AsientosView',
    'ReportesView',
    'ConfiguracionView'
]