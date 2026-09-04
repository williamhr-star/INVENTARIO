"""
Modelo de Producto
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Producto:
    """Modelo de producto/inventario"""
    id: Optional[int] = None
    codigo: str = ""
    nombre: str = ""
    categoria: str = ""
    unidad_medida: str = "unidad"
    stock_actual: float = 0.0
    stock_minimo: float = 0.0
    stock_maximo: float = 1000.0
    precio_costo: float = 0.0
    precio_venta: float = 0.0
    ubicacion: str = ""
    fecha_creacion: str = None
    ultima_actualizacion: str = None
    
    def __post_init__(self):
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.now().isoformat()
        if not self.ultima_actualizacion:
            self.ultima_actualizacion = datetime.now().isoformat()
    
    @property
    def valor_inventario(self) -> float:
        """Valor total del inventario de este producto"""
        return self.stock_actual * self.precio_costo
    
    @property
    def margen_ganancia(self) -> float:
        """Margen de ganancia en porcentaje"""
        if self.precio_costo == 0:
            return 0
        return ((self.precio_venta - self.precio_costo) / self.precio_costo) * 100
    
    @property
    def stock_bajo(self) -> bool:
        """Indica si el stock está por debajo del mínimo"""
        return self.stock_actual < self.stock_minimo
    
    @property
    def stock_alto(self) -> bool:
        """Indica si el stock está por encima del máximo"""
        return self.stock_actual > self.stock_maximo
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'unidad_medida': self.unidad_medida,
            'stock_actual': self.stock_actual,
            'stock_minimo': self.stock_minimo,
            'stock_maximo': self.stock_maximo,
            'precio_costo': self.precio_costo,
            'precio_venta': self.precio_venta,
            'ubicacion': self.ubicacion,
            'fecha_creacion': self.fecha_creacion,
            'ultima_actualizacion': self.ultima_actualizacion
        }