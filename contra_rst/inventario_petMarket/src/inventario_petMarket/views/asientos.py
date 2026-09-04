"""
Vista para crear asientos contables manuales
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime
from ..styles import COLORS
from ..widgets import Card, ActionButton, Toast


class AsientosView:
    """Vista para la creación de asientos contables"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.main_box = None
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=15))
        
        # ========== ENCABEZADO ==========
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("➕ Crear Asiento Contable", 
                    style=Pack(font_size=24, font_weight="bold", color=COLORS['primary']))
        )
        self.main_box.add(header)
        
        # ========== FORMULARIO ==========
        form = Card(
            toga.Box(style=Pack(direction=COLUMN, gap=10)),
            padding=20
        )
        
        # Fecha
        form.add(toga.Label("Fecha:", style=Pack(font_weight="bold")))
        self.fecha_input = toga.DateInput(value=datetime.now(), style=Pack(width=200))
        form.add(self.fecha_input)
        
        # Descripción
        form.add(toga.Label("Descripción:", style=Pack(font_weight="bold")))
        self.descripcion_input = toga.TextInput(placeholder="Ej: Pago de proveedor", style=Pack(width=400))
        form.add(self.descripcion_input)
        
        # Cuenta
        form.add(toga.Label("Cuenta:", style=Pack(font_weight="bold")))
        self.cuenta_input = toga.TextInput(placeholder="Código (ej: 1105)", style=Pack(width=150))
        form.add(self.cuenta_input)
        
        # Nombre cuenta
        form.add(toga.Label("Nombre de la cuenta:", style=Pack(font_weight="bold")))
        self.nombre_cuenta_input = toga.TextInput(placeholder="Ej: Caja", style=Pack(width=300))
        form.add(self.nombre_cuenta_input)
        
        # Débito y Crédito
        row = toga.Box(style=Pack(direction=ROW, gap=20))
        self.debito_input = toga.NumberInput(
            value=0.00, min=0, style=Pack(width=150)
        )
        row.add(
            toga.Box(style=Pack(direction=COLUMN), children=[
                toga.Label("Débito:", style=Pack(font_weight="bold")),
                self.debito_input,
            ])
        )
        self.credito_input = toga.NumberInput(
            value=0.00, min=0, style=Pack(width=150)
        )
        row.add(
            toga.Box(style=Pack(direction=COLUMN), children=[
                toga.Label("Crédito:", style=Pack(font_weight="bold")),
                self.credito_input,
            ])
        )
        form.add(row)
        
        # Botón guardar
        form.add(
            ActionButton("💾 Guardar Asiento", self._guardar_asiento, "💾", COLORS['success'])
        )
        
        self.main_box.add(form)
        
        # ========== ÚLTIMOS ASIENTOS ==========
        self.main_box.add(
            toga.Label("📋 Últimos asientos creados", 
                    style=Pack(font_size=18, font_weight="bold", margin_top=20))
        )
        self._actualizar_ultimos_asientos()
        
        return self.main_box
    
    def _guardar_asiento(self, widget):
        """Guarda el asiento en la base de datos"""
        fecha = self.fecha_input.value
        descripcion = self.descripcion_input.value
        cuenta = self.cuenta_input.value
        nombre_cuenta = self.nombre_cuenta_input.value
        debito = float(self.debito_input.value or 0)
        credito = float(self.credito_input.value or 0)
        
        # Validaciones
        if not cuenta:
            Toast(self.app.main_window, "⚠️ Ingrese el código de la cuenta", "warning").show()
            return
        
        if debito == 0 and credito == 0:
            Toast(self.app.main_window, "⚠️ Ingrese débito o crédito", "warning").show()
            return
        
        if debito > 0 and credito > 0:
            Toast(self.app.main_window, "⚠️ No puede tener débito y crédito simultáneamente", "error").show()
            return
        
        # Guardar
        datos = {
            'fecha': fecha.strftime("%Y-%m-%d"),
            'descripcion': descripcion or "Asiento manual",
            'cuenta': cuenta,
            'nombre_cuenta': nombre_cuenta or cuenta,
            'debito': debito,
            'credito': credito,
            'tipo_movimiento': 'MANUAL',
            'usuario': 'Admin'
        }
        
        self.db.crear_asiento(datos)
        Toast(self.app.main_window, "✅ Asiento creado exitosamente", "success").show()
        
        # Limpiar campos
        self.descripcion_input.value = ""
        self.cuenta_input.value = ""
        self.nombre_cuenta_input.value = ""
        self.debito_input.value = 0
        self.credito_input.value = 0
        
        self._actualizar_ultimos_asientos()
    
    def _actualizar_ultimos_asientos(self):
        """Actualiza la lista de últimos asientos"""
        # Crear el contenedor una sola vez y reemplazar su contenido en cada
        # actualización para evitar que los registros se dupliquen.
        if getattr(self, "ultimos_asientos_box", None) is None:
            self.ultimos_asientos_box = toga.Box(
                style=Pack(direction=COLUMN, gap=5, flex=1)
            )
            self.main_box.add(self.ultimos_asientos_box)
        else:
            for child in list(self.ultimos_asientos_box.children):
                self.ultimos_asientos_box.remove(child)

        asientos = []
        for nombre in ("obtener_ultimos_asientos", "listar_asientos", "obtener_asientos"):
            consulta = getattr(self.db, nombre, None)
            if callable(consulta):
                try:
                    asientos = list(consulta() or [])
                except TypeError:
                    asientos = list(consulta(limit=10) or [])
                break

        if not asientos:
            self.ultimos_asientos_box.add(
                toga.Label("No hay asientos creados todavía.", style=Pack(padding=5))
            )
            return

        for asiento in asientos[:10]:
            def obtener(nombre, defecto=""):
                if isinstance(asiento, dict):
                    return asiento.get(nombre, defecto)
                return getattr(asiento, nombre, defecto)

            fecha = obtener("fecha")
            cuenta = obtener("cuenta")
            descripcion = obtener("descripcion", "Asiento manual")
            debito = float(obtener("debito", 0) or 0)
            credito = float(obtener("credito", 0) or 0)
            importe = (
                f"Débito: {debito:.2f}" if debito else f"Crédito: {credito:.2f}"
            )
            self.ultimos_asientos_box.add(
                toga.Label(
                    f"{fecha} · {cuenta} · {descripcion} · {importe}",
                    style=Pack(padding=5)
                )
            )