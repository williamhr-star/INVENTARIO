"""
Vista de contabilidad - Libro Diario, Mayor, RST, IVA
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime
from ..styles import COLORS
from ..widgets import Card, DataTable, StatCard


class ContabilidadView:
    """Vista de contabilidad con múltiples secciones"""
    
    def __init__(self, app, db_manager, seccion='diario'):
        self.app = app
        self.db = db_manager
        self.seccion = seccion  # 'diario', 'mayor', 'conciliacion', 'rst_iva', 'puc'
        self.main_box = None
        self.movimientos_box = None
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=15))
        
        # ========== ENCABEZADO ==========
        titulos = {
            'diario': '📒 Libro Diario',
            'mayor': '📈 Libro Mayor',
            'conciliacion': '📄 Conciliación',
            'rst_iva': '🧾 RST · IVA',
            'puc': '📋 Plan Único de Cuentas (PUC)'
        }
        
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label(titulos.get(self.seccion, '📊 Contabilidad'), 
                      style=Pack(font_size=24, font_weight="bold", color=COLORS['primary']))
        )
        
        # Selector de sección
        seccion_selector = toga.Selection(
            items=list(titulos.values()),
            style=Pack(width=250, padding=10)
        )
        seccion_selector.value = titulos.get(self.seccion)
        seccion_selector.on_select = self._cambiar_seccion
        header.add(seccion_selector)
        
        self.main_box.add(header)
        
        # ========== CONTENIDO SEGÚN SECCIÓN ==========
        if self.seccion == 'diario':
            self._build_libro_diario()
        elif self.seccion == 'mayor':
            self._build_libro_mayor()
        elif self.seccion == 'conciliacion':
            self._build_conciliacion()
        elif self.seccion == 'rst_iva':
            self._build_rst_iva()
        elif self.seccion == 'puc':
            self._build_puc()
        
        return self.main_box
    
    def _cambiar_seccion(self, widget):
        """Cambia la sección actual"""
        titulos = {
            '📒 Libro Diario': 'diario',
            '📈 Libro Mayor': 'mayor',
            '📄 Conciliación': 'conciliacion',
            '🧾 RST · IVA': 'rst_iva',
            '📋 Plan Único de Cuentas (PUC)': 'puc'
        }
        self.seccion = titulos.get(widget.value, 'diario')
        # Reconstruir vista
        self.app.show_view(ContabilidadView, self.seccion)
    
    def _build_libro_diario(self):
        """Construye la vista del Libro Diario"""
        # Selector de período
        period = toga.Box(style=Pack(direction=ROW, gap=10, padding=10))
        period.add(
            toga.Label("Período:", style=Pack(font_weight="bold")),
            toga.DateInput(value=datetime(2026, 1, 1), style=Pack(width=150)),
            toga.Label("→"),
            toga.DateInput(value=datetime.now(), style=Pack(width=150)),
            toga.Button("Filtrar", style=Pack(background_color=COLORS['primary'], color=COLORS['white']))
        )
        self.main_box.add(period)
        
        # Tabla de asientos
        asientos = self.db.obtener_ultimos_asientos(50)
        if asientos:
            columns = ["Fecha", "Descripción", "Cuenta", "Débito", "Crédito"]
            data = []
            for a in asientos:
                data.append({
                    "Fecha": a['fecha'][:10],
                    "Descripción": a['descripcion'][:40],
                    "Cuenta": f"{a['cuenta']} - {a['nombre_cuenta'][:20]}",
                    "Débito": f"${a['debito']:,.0f}" if a['debito'] > 0 else "",
                    "Crédito": f"${a['credito']:,.0f}" if a['credito'] > 0 else ""
                })
            table = DataTable(columns, data)
            self.main_box.add(table)
        else:
            self.main_box.add(
                toga.Label("No hay asientos registrados", 
                          style=Pack(padding=40, color=COLORS['gray_600'], text_align="center"))
            )
    
    def _build_libro_mayor(self):
        """Construye la vista del Libro Mayor"""
        self.main_box.add(
            toga.Label("📈 Libro Mayor por Cuenta", 
                      style=Pack(font_size=18, font_weight="bold"))
        )
        
        # Selector de cuenta
        cuentas = ['1105 - Caja', '1305 - Bancos', '1435 - Inventario', 
                   '2105 - Proveedores', '3115 - Capital', '4135 - Ingresos', '6135 - Costo de Ventas']
        
        cuenta_selector = toga.Selection(
            items=cuentas,
            style=Pack(width=300, padding=10)
        )
        cuenta_selector.on_select = self._mostrar_movimientos_cuenta
        self.main_box.add(cuenta_selector)
        
        # Tabla de movimientos
        self.movimientos_box = toga.Box(style=Pack(direction=COLUMN))
        self.main_box.add(self.movimientos_box)
    
    def _mostrar_movimientos_cuenta(self, widget):
        """Muestra los movimientos de una cuenta"""
        self.movimientos_box.clear()
        
        codigo = widget.value.split(' - ')[0]
        # Buscar asientos de esta cuenta
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT fecha, descripcion, debito, credito FROM asientos WHERE cuenta LIKE ? ORDER BY fecha DESC LIMIT 20",
            (f"{codigo}%",)
        )
        resultados = cursor.fetchall()
        conn.close()
        
        if resultados:
            columns = ["Fecha", "Descripción", "Débito", "Crédito"]
            data = []
            for r in resultados:
                data.append({
                    "Fecha": r[0][:10],
                    "Descripción": r[1][:40],
                    "Débito": f"${r[2]:,.0f}" if r[2] > 0 else "",
                    "Crédito": f"${r[3]:,.0f}" if r[3] > 0 else ""
                })
            table = DataTable(columns, data)
            self.movimientos_box.add(table)
        else:
            self.movimientos_box.add(
                toga.Label("No hay movimientos para esta cuenta", 
                          style=Pack(padding=20, color=COLORS['gray_600']))
            )
    
    def _build_conciliacion(self):
        """Construye la vista de conciliación"""
        self.main_box.add(
            toga.Label("📄 Conciliación Bancaria", 
                      style=Pack(font_size=18, font_weight="bold"))
        )
        
        # Formulario de conciliación
        form = toga.Box(style=Pack(direction=COLUMN, gap=10))
        form.add(
            toga.Label("Saldo en Banco:", style=Pack(font_weight="bold")),
            toga.NumberInput(value=0.00, style=Pack(width=200)),
            toga.Label("Saldo en Libros:", style=Pack(font_weight="bold")),
            toga.NumberInput(value=0.00, style=Pack(width=200)),
            toga.Button("Calcular Diferencia", style=Pack(background_color=COLORS['primary'], color=COLORS['white']))
        )
        self.main_box.add(Card(form))
    
    def _build_rst_iva(self):
        """Construye la vista de RST e IVA"""
        self.main_box.add(
            toga.Label("🧾 RST · Régimen Simple", 
                      style=Pack(font_size=18, font_weight="bold"))
        )
        
        # Obtener datos
        resumen = self.db.obtener_resumen_periodo("2026-01-01", datetime.now().strftime("%Y-%m-%d"))
        
        # Tarjetas de RST
        cards = [
            StatCard("Ingresos", f"${resumen['ingresos']:,.0f}", COLORS['primary'], "📊"),
            StatCard("IVA (19%)", f"${resumen['ingresos'] * 0.19:,.0f}", COLORS['info'], "🧾"),
            StatCard("RST (2.5%)", f"${resumen['rst_estimado']:,.0f}", COLORS['warning'], "📋"),
        ]
        self.main_box.add(toga.Box(style=Pack(direction=ROW, gap=20), children=cards))
        
        # Tabla de tarifas
        self.main_box.add(
            toga.Label("Tarifas por Actividad", 
                      style=Pack(font_size=16, font_weight="bold", margin_top=20))
        )
        
        tarifas = [
            ["Actividad", "Tarifa RST"],
            ["Comercio al por menor", "2.5%"],
            ["Servicios", "3.0%"],
            ["Industria", "2.0%"],
            ["Agricultura", "1.5%"],
        ]
        
        # Crear tabla simple
        table = toga.Box(style=Pack(direction=COLUMN, background_color=COLORS['white'], padding=5))
        for i, row in enumerate(tarifas):
            r = toga.Box(style=Pack(direction=ROW, padding=5, background_color=COLORS['gray_50'] if i % 2 == 0 else COLORS['white']))
            for col in row:
                r.add(toga.Label(col, style=Pack(width=150, font_weight="bold" if i == 0 else "normal")))
            table.add(r)
        self.main_box.add(table)
    
    def _build_puc(self):
        """Construye la vista del Plan Único de Cuentas"""
        self.main_box.add(
            toga.Label("📋 Plan Único de Cuentas (PUC)", 
                      style=Pack(font_size=18, font_weight="bold"))
        )
        
        # Categorías del PUC
        puc_categorias = [
            ("1", "Activo", [
                ("1105", "Caja"),
                ("1305", "Bancos"),
                ("1435", "Inventario"),
            ]),
            ("2", "Pasivo", [
                ("2105", "Proveedores"),
                ("2205", "Obligaciones Laborales"),
            ]),
            ("3", "Patrimonio", [
                ("3115", "Capital"),
            ]),
            ("4", "Ingresos", [
                ("4135", "Ingresos"),
            ]),
            ("5", "Gastos Operativos", [
                ("5105", "Gastos de Personal"),
                ("5205", "Gastos Generales"),
            ]),
            ("6", "Costo de Ventas", [
                ("6135", "Costo de Ventas"),
            ]),
        ]
        
        for categoria, nombre, cuentas in puc_categorias:
            # Encabezado de categoría
            self.main_box.add(
                toga.Label(f"{categoria} - {nombre}", 
                          style=Pack(font_size=16, font_weight="bold", color=COLORS['primary'], margin_top=10))
            )
            
            # Lista de cuentas
            for codigo, nombre_cuenta in cuentas:
                self.main_box.add(
                    toga.Label(f"  {codigo} - {nombre_cuenta}", 
                              style=Pack(font_size=13, margin_left=20))
                )