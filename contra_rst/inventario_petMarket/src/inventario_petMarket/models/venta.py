"""
Modelo de Venta
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class DetalleVenta:
    """Detalle de una venta"""
    producto_id: int
    cantidad: float
    precio_unitario: float
    descuento: float = 0.0
    
    @property
    def subtotal(self) -> float:
        """Subtotal del detalle"""
        return self.cantidad * self.precio_unitario * (1 - self.descuento / 100)


@dataclass
class Venta:
    """Modelo de venta"""
    id: Optional[int] = None
    fecha: str = None
    cliente: str = "Cliente General"
    tipo_comprobante: str = "Boleta"
    numero_comprobante: str = ""
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    estado: str = "Pagada"
    usuario: str = "Admin"
    detalles: List[DetalleVenta] = None
    
    def __post_init__(self):
        if not self.fecha:
            self.fecha = datetime.now().isoformat()
        if self.detalles is None:
            self.detalles = []
    
    @property
    def iva_porcentaje(self) -> float:
        """Porcentaje de IVA aplicado"""
        return 19.0
    
    def calcular_totales(self):
        """Calcula subtotal, IVA y total"""
        self.subtotal = sum(d.subtotal for d in self.detalles)
        self.iva = self.subtotal * (self.iva_porcentaje / 100)
        self.total = self.subtotal + self.iva
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'fecha': self.fecha,
            'cliente': self.cliente,
            'tipo_comprobante': self.tipo_comprobante,
            'numero_comprobante': self.numero_comprobante,
            'subtotal': self.subtotal,
            'iva': self.iva,
            'total': self.total,
            'estado': self.estado,
            'usuario': self.usuario
        }