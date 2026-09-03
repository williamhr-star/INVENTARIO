"""
Dashboard - Pantalla principal de resumen
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime
from ..styles import COLORS
from ..widgets import StatCard, Card, DataTable, Toast


class DashboardView:
    """Vista principal del dashboard"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.fecha_desde = "2026-01-01"
        self.fecha_hasta = datetime.now().strftime("%Y-%m-%d")
        self.main_box = None
        self.resumen_box = None
        self.tabla_box = None
        self.cuentas_box = None
    
    def build(self):
        """Construye la vista del dashboard"""
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, padding=20))
        
        # ========== ENCABEZADO ==========
        header = toga.Box(style=Pack(direction=ROW, padding=10))
        header.add(
            toga.Label("📊 Resumen del período", 
                    style=Pack(font_size=24, font_weight="bold", color=COLORS['text_primary']))
        )
        
        # Botones de acción
        actions = toga.Box(style=Pack(direction=ROW, padding=10))
        actions.add(
            toga.Button(
                "📄 Generar PDF",
                on_press=self.generar_pdf,
                style=Pack(background_color=COLORS['danger'], color=COLORS['white'], padding=10)
            )
        )
        actions.add(
            toga.Button(
                "➕ Asiento",
                on_press=self.crear_asiento,
                style=Pack(background_color=COLORS['primary'], color=COLORS['white'], padding=10)
            )
        )
        header.add(actions)
        self.main_box.add(header)
        
        # ========== SELECTOR DE PERÍODO ==========
        period_box = Card(
            toga.Box(style=Pack(direction=ROW, gap=10)),
            padding=10
        )
        period_box.add(
            toga.Label("Período:", style=Pack(font_weight="bold")),
            toga.TextInput(value=self.fecha_desde, style=Pack(width=120), on_change=self._cambiar_desde),
            toga.Label("→", style=Pack(padding=5)),
            toga.TextInput(value=self.fecha_hasta, style=Pack(width=120), on_change=self._cambiar_hasta),
            toga.Button(
                "Actualizar",
                on_press=self.actualizar_dashboard,
                style=Pack(background_color=COLORS['primary'], color=COLORS['white'])
            )
        )
        self.main_box.add(period_box)
        
        # ========== TARJETAS DE RESUMEN ==========
        self.resumen_box = toga.Box(style=Pack(direction=ROW, gap=20, padding=10))
        self._actualizar_tarjetas()
        self.main_box.add(self.resumen_box)
        
        # ========== TABLA DE ASIENTOS ==========
        self.main_box.add(
            toga.Label("📋 Últimos asientos registrados", 
                      style=Pack(font_size=18, font_weight="bold", margin_top=20))
        )
        self.tabla_box = toga.Box(style=Pack(direction=COLUMN))
        self._actualizar_tabla_asientos()
        self.main_box.add(self.tabla_box)
        
        # ========== ESTADO DE CUENTAS ==========
        self.main_box.add(
            toga.Label("💰 Estado de cuentas clave", 
                      style=Pack(font_size=18, font_weight="bold", margin_top=20))
        )
        self.cuentas_box = toga.Box(style=Pack(direction=COLUMN, gap=5))
        self._actualizar_cuentas()
        self.main_box.add(self.cuentas_box)
        
        # ========== RESÚMENES ==========
        # Menú de resúmenes (igual que en la imagen)
        resumen_menu = toga.Box(style=Pack(direction=ROW, gap=20, margin_top=20))
        for item in ["Libro Diario", "Libro Mayor", "Conciliación", "RST · IVA", "Reportes PDF", "PUC"]:
            btn = toga.Button(
                f"📄 {item}",
                on_press=self._ir_resumen,
                style=Pack(background_color=COLORS['gray_200'], color=COLORS['text_primary'])
            )
            btn.item = item
            resumen_menu.add(btn)
        self.main_box.add(resumen_menu)
        
        return self.main_box
    
    def _actualizar_tarjetas(self):
        """Actualiza las tarjetas de resumen"""
        self.resumen_box.clear()
        
        resumen = self.db.obtener_resumen_periodo(self.fecha_desde, self.fecha_hasta)
        
        tarjetas = [
            ("Ingresos", f"${resumen['ingresos']:,.0f}", COLORS['success'], "📈"),
            ("Gastos", f"${resumen['gastos']:,.0f}", COLORS['danger'], "📉"),
            ("Utilidad neta", f"${resumen['utilidad_neta']:,.0f}", COLORS['primary'], "💰"),
            ("RST estimado", f"${resumen['rst_estimado']:,.0f}", COLORS['warning'], "🧾"),
        ]
        
        for titulo, valor, color, icono in tarjetas:
            card = StatCard(titulo, valor, color, icono)
            self.resumen_box.add(card)
    
    def _actualizar_tabla_asientos(self):
        """Actualiza la tabla de asientos"""
        self.tabla_box.clear()
        
        asientos = self.db.obtener_ultimos_asientos(10)
        
        if not asientos:
            self.tabla_box.add(
                toga.Label("Sin movimientos aún.", 
                          style=Pack(padding=20, color=COLORS['gray_600'], text_align="center"))
            )
            return
        
        # Crear tabla con DataTable widget
        columns = ["Fecha", "Descripción", "Cuenta", "Débito", "Crédito"]
        data = []
        for a in asientos:
            data.append({
                "Fecha": a['fecha'][:10],
                "Descripción": a['descripcion'][:30],
                "Cuenta": f"{a['cuenta']} - {a['nombre_cuenta'][:15]}",
                "Débito": f"${a['debito']:,.0f}" if a['debito'] > 0 else "",
                "Crédito": f"${a['credito']:,.0f}" if a['credito'] > 0 else ""
            })
        
        table = DataTable(columns, data)
        self.tabla_box.add(table)
    
    def _actualizar_cuentas(self):
        """Actualiza el estado de cuentas clave"""
        self.cuentas_box.clear()
        
        cuentas = self.db.obtener_cuentas_clave()
        
        for codigo, info in cuentas.items():
            row = toga.Box(
                style=Pack(
                    direction=ROW,
                    padding=8,
                )
            )
            row.add(
                toga.Label(f"{codigo} - {info['nombre']}", style=Pack(width=250)),
                toga.Label(
                    f"${info['saldo']:,.0f}",
                    style=Pack(
                        color=COLORS['success'] if info['saldo'] >= 0 else COLORS['danger'],
                        font_weight="bold"
                    )
                )
            )
            self.cuentas_box.add(row)
    
    def _cambiar_desde(self, widget):
        self.fecha_desde = widget.value
    
    def _cambiar_hasta(self, widget):
        self.fecha_hasta = widget.value
    
    def actualizar_dashboard(self, _widget):
        """Actualiza todo el dashboard"""
        self._actualizar_tarjetas()
        self._actualizar_tabla_asientos()
        self._actualizar_cuentas()
        Toast(self.app.main_window, "✅ Dashboard actualizado", "success").show()
    
    def generar_pdf(self, _widget):
        """Genera el PDF de resumen"""
        from ..pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator(self.db.db_path)
        filename = pdf_gen.generar_estado_resultados(self.fecha_desde, self.fecha_hasta)
        Toast(self.app.main_window, f"✅ PDF generado: {filename}", "success").show()
    
    def crear_asiento(self, _widget):
        """Abre el diálogo para crear un nuevo asiento"""
        self.app.show_asientos()
    
    def _ir_resumen(self, widget):
        """Navega a la sección de resumen"""
        item = getattr(widget, 'item', '')
        if item == "Libro Diario":
            self.app.show_libro_diario()
        elif item == "Libro Mayor":
            self.app.show_libro_mayor()
        elif item == "Conciliación":
            self.app.show_conciliacion()
        elif item == "RST · IVA":
            self.app.show_rst_iva()
        elif item == "Reportes PDF":
            self.app.show_reportes()
        elif item == "PUC":
            self.app.show_puc()