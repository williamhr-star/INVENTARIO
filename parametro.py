"""
Modelo de Parámetro
"""
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Parametro:
    """Modelo de parámetro del sistema"""
    id: Optional[int] = None
    clave: str = ""
    valor: str = ""
    descripcion: str = ""
    
    @property
    def valor_int(self) -> int:
        """Valor como entero"""
        try:
            return int(self.valor)
        except ValueError:
            return 0
    
    @property
    def valor_float(self) -> float:
        """Valor como float"""
        try:
            return float(self.valor)
        except ValueError:
            return 0.0
    
    @property
    def valor_bool(self) -> bool:
        """Valor como booleano"""
        return self.valor.lower() in ('true', '1', 'yes', 'si')
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion
        }