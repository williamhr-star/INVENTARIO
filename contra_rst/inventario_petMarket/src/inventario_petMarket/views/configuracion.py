"""
Vista de configuración del sistema
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..styles import COLORS
from ..widgets import Card, ActionButton, Toast


class ConfiguracionView:
    """Vista de configuración de la aplicación"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.main_box = None
        
        # Inicializar atributos
        self.nombre_input = None
        self.nit_input = None
        self.direccion_input = None
        self.telefono_input = None
        self.iva_input = None
        self.rst_input = None
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=15))
        
        # ========== ENCABEZADO ==========
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("⚙️ Configuración", 
                      style=Pack(font_size=24, font_weight="bold", color=COLORS['primary']))
        )
        self.main_box.add(header)
        
        # ========== INFORMACIÓN DE LA EMPRESA ==========
        empresa_card = Card(
            toga.Box(style=Pack(direction=COLUMN, gap=10)),
            margin=20
        )
        empresa_card.add(
            toga.Label("🏢 Datos de la Empresa", style=Pack(font_size=16, font_weight="bold"))
        )
        
        # ✅ Usar hint_text en lugar de placeholder
        self.nombre_input = toga.TextInput(style=Pack(width=400))
        self.nombre_input.hint_text = "Nombre de la empresa"
        
        self.nit_input = toga.TextInput(style=Pack(width=200))
        self.nit_input.hint_text = "NIT"
        
        self.direccion_input = toga.TextInput(style=Pack(width=400))
        self.direccion_input.hint_text = "Dirección"
        
        self.telefono_input = toga.TextInput(style=Pack(width=200))
        self.telefono_input.hint_text = "Teléfono"

        def campo(etiqueta, control):
            fila = toga.Box(style=Pack(direction=ROW, gap=10))
            fila.add(toga.Label(etiqueta, style=Pack(width=130, color=COLORS['text_primary'])), control)
            return fila
        
        empresa_card.add(
            campo("Razón social", self.nombre_input),
            campo("NIT", self.nit_input),
            campo("Dirección", self.direccion_input),
            campo("Teléfono", self.telefono_input),
            ActionButton("💾 Guardar Datos", self._guardar_empresa, "💾", COLORS['success'])
        )
        
        self.main_box.add(empresa_card)
        
        # ========== PARÁMETROS CONTABLES ==========
        params_card = Card(
            toga.Box(style=Pack(direction=COLUMN, gap=10)),
            margin=20
        )
        params_card.add(
            toga.Label("📊 Parámetros Contables", style=Pack(font_size=16, font_weight="bold"))
        )
        
        # ✅ NumberInput sin placeholder, usar hint_text
        self.iva_input = toga.NumberInput(value=19, style=Pack(width=150))
        self.iva_input.hint_text = "IVA (%)"
        
        self.rst_input = toga.NumberInput(value=2.5, style=Pack(width=150))
        self.rst_input.hint_text = "RST (%)"
        
        params_card.add(
            toga.Box(style=Pack(direction=ROW, gap=20), children=[
                toga.Label("IVA %", style=Pack(width=130, font_weight="bold", color=COLORS['text_primary'])),
                self.iva_input
            ]),
            toga.Box(style=Pack(direction=ROW, gap=20), children=[
                toga.Label("Tarifa RST %", style=Pack(width=130, font_weight="bold", color=COLORS['text_primary'])),
                self.rst_input
            ]),
            ActionButton("💾 Guardar Parámetros", self._guardar_parametros, "💾", COLORS['success'])
        )
        
        self.main_box.add(params_card)
        
        # ========== SISTEMA ==========
        system_card = Card(
            toga.Box(style=Pack(direction=COLUMN, gap=10)),
            margin=20
        )
        system_card.add(
            toga.Label("🔄 Sistema", style=Pack(font_size=16, font_weight="bold"))
        )
        
        system_card.add(
            toga.Button(
                "📤 Sincronizar con OneDrive",
                on_press=self._sincronizar,
                style=Pack(background_color=COLORS['primary'], color=COLORS['white'])
            )
        )
        system_card.add(
            toga.Button(
                "📥 Cargar desde OneDrive",
                on_press=self._cargar_desde_onedrive,
                style=Pack(background_color=COLORS['info'], color=COLORS['white'])
            )
        )
        
        self.main_box.add(system_card)
        
        # ========== INFORMACIÓN ==========
        info_card = Card(
            toga.Box(style=Pack(direction=COLUMN, gap=5)),
            margin=15
        )
        info_card.add(
            toga.Label("ℹ️ Información del Sistema", style=Pack(font_size=14, font_weight="bold")),
            toga.Label("Inventario PetMarket v1.0.0", style=Pack(color=COLORS['gray_600'])),
            toga.Label("Desarrollado con BeeWare y Python", style=Pack(color=COLORS['gray_600'])),
            toga.Label("Base de datos: SQLite + OneDrive Sync", style=Pack(color=COLORS['gray_600']))
        )
        self.main_box.add(info_card)
        
        # Cargar datos actuales
        self._cargar_datos()
        
        return self.main_box
    
    def _cargar_datos(self):
        """Carga los datos actuales de la base de datos"""
        try:
            conn = self.db.conectar()
            cursor = conn.cursor()
            
            cursor.execute("SELECT clave, valor FROM parametros")
            params = cursor.fetchall()
            conn.close()
            
            for clave, valor in params:
                if clave == 'EMPRESA_NOMBRE' and self.nombre_input:
                    self.nombre_input.value = valor
                elif clave == 'EMPRESA_NIT' and self.nit_input:
                    self.nit_input.value = valor
                elif clave == 'EMPRESA_DIRECCION' and self.direccion_input:
                    self.direccion_input.value = valor
                elif clave == 'EMPRESA_TELEFONO' and self.telefono_input:
                    self.telefono_input.value = valor
                elif clave == 'IVA' and self.iva_input:
                    self.iva_input.value = float(valor)
                elif clave == 'RST_TARIFA' and self.rst_input:
                    self.rst_input.value = float(valor)
        except Exception:
            pass
    
    def _guardar_empresa(self, _widget):
        """Guarda los datos de la empresa"""
        try:
            conn = self.db.conectar()
            cursor = conn.cursor()
            
            datos = [
                ('EMPRESA_NOMBRE', self.nombre_input.value if self.nombre_input else ''),
                ('EMPRESA_NIT', self.nit_input.value if self.nit_input else ''),
                ('EMPRESA_DIRECCION', self.direccion_input.value if self.direccion_input else ''),
                ('EMPRESA_TELEFONO', self.telefono_input.value if self.telefono_input else ''),
            ]
            
            for clave, valor in datos:
                cursor.execute(
                    "UPDATE parametros SET valor = ? WHERE clave = ?",
                    (valor, clave)
                )
            
            conn.commit()
            conn.close()
            Toast(self.app.main_window, "✅ Datos de empresa guardados", "success").show()
        except Exception as e:
            Toast(self.app.main_window, f"❌ Error: {str(e)}", "error").show()
    
    def _guardar_parametros(self, _widget):
        """Guarda los parámetros contables"""
        try:
            conn = self.db.conectar()
            cursor = conn.cursor()
            
            if self.iva_input:
                cursor.execute(
                    "UPDATE parametros SET valor = ? WHERE clave = 'IVA'",
                    (str(self.iva_input.value),)
                )
            if self.rst_input:
                cursor.execute(
                    "UPDATE parametros SET valor = ? WHERE clave = 'RST_TARIFA'",
                    (str(self.rst_input.value),)
                )
            
            conn.commit()
            conn.close()
            Toast(self.app.main_window, "✅ Parámetros guardados", "success").show()
        except Exception as e:
            Toast(self.app.main_window, f"❌ Error: {str(e)}", "error").show()
    
    def _sincronizar(self, _widget):
        """Sincroniza con OneDrive"""
        success, msg = self.app.sync_manager.sincronizar_db()
        Toast(self.app.main_window, msg, "success" if success else "error").show()
    
    def _cargar_desde_onedrive(self, _widget):
        """Carga desde OneDrive"""
        success, msg = self.app.sync_manager.cargar_db()
        Toast(self.app.main_window, msg, "success" if success else "warning").show()