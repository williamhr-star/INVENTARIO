"""
Modelo de Asiento Contable
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Asiento:
    """Modelo de asiento contable"""
    id: Optional[int] = None
    fecha: str = None
    descripcion: str = ""
    cuenta: str = ""
    nombre_cuenta: str = ""
    debito: float = 0.0
    credito: float = 0.0
    documento_referencia: str = ""
    tipo_movimiento: str = "MANUAL"
    usuario: str = "Admin"
    
    def __post_init__(self):
        if not self.fecha:
            self.fecha = datetime.now().isoformat()
    
    @property
    def es_debito(self) -> bool:
        """Indica si es un asiento de débito"""
        return self.debito > 0
    
    @property
    def es_credito(self) -> bool:
        """Indica si es un asiento de crédito"""
        return self.credito > 0
    
    @property
    def monto(self) -> float:
        """Monto del asiento (débito o crédito)"""
        return self.debito if self.debito > 0 else self.credito
    
    @property
    def tipo(self) -> str:
        """Tipo de asiento (Débito/Crédito)"""
        if self.debito > 0:
            return "Débito"
        elif self.credito > 0:
            return "Crédito"
        return "N/A"
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'fecha': self.fecha,
            'descripcion': self.descripcion,
            'cuenta': self.cuenta,
            'nombre_cuenta': self.nombre_cuenta,
            'debito': self.debito,
            'credito': self.credito,
            'documento_referencia': self.documento_referencia,
            'tipo_movimiento': self.tipo_movimiento,
            'usuario': self.usuario
        }