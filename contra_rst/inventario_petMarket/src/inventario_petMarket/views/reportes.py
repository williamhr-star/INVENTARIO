"""
Vista de reportes PDF
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime
from ..styles import COLORS
from ..widgets import Card, ActionButton, Toast


class ReportesView:
    """Vista de generación de reportes PDF"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.main_box = None
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=15))
        
        # ========== ENCABEZADO ==========
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("📎 Reportes PDF", 
                      style=Pack(font_size=24, font_weight="bold", color=COLORS['primary']))
        )
        self.main_box.add(header)
        
        # ========== TARJETAS DE REPORTES ==========
        reportes = [
            ("📊", "Estado de Resultados", "Resumen financiero del período", self._generar_estado_resultados),
            ("📦", "Inventario Valorizado", "Lista de productos con valor total", self._generar_inventario),
            ("💰", "Libro Diario", "Todos los asientos del período", self._generar_libro_diario),
            ("🧾", "RST e IVA", "Resumen de impuestos", self._generar_rst_iva),
        ]
        
        for icono, titulo, desc, on_click in reportes:
            card = Card(
                toga.Box(style=Pack(direction=COLUMN, gap=5)),
                padding=15,
                width=350
            )
            card.add(
                toga.Label(f"{icono} {titulo}", style=Pack(font_size=16, font_weight="bold")),
                toga.Label(desc, style=Pack(color=COLORS['gray_600'], font_size=12)),
                ActionButton("📄 Generar PDF", on_click, "📄", COLORS['danger'])
            )
            self.main_box.add(card)
        
        return self.main_box
    
    def _generar_estado_resultados(self, widget):
        """Genera el estado de resultados"""
        from ..pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator(self.db.db_path)
        filename = pdf_gen.generar_estado_resultados("2026-01-01", datetime.now().strftime("%Y-%m-%d"))
        Toast(self.app.main_window, f"✅ PDF generado: {filename}", "success").show()
    
    def _generar_inventario(self, widget):
        """Genera el reporte de inventario"""
        from ..pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator(self.db.db_path)
        filename = pdf_gen.generar_inventario_valorizado()
        Toast(self.app.main_window, f"✅ PDF generado: {filename}", "success").show()
    
    def _generar_libro_diario(self, widget):
        """Genera el libro diario en PDF"""
        from ..pdf_generator import PDFGenerator
        filename = PDFGenerator(self.db.db_path).generar_libro_diario("2026-01-01", datetime.now().strftime("%Y-%m-%d"))
        Toast(self.app.main_window, f"PDF generado: {filename}", "success").show()
    
    def _generar_rst_iva(self, widget):
        """Genera el reporte de RST e IVA"""
        from ..pdf_generator import PDFGenerator
        filename = PDFGenerator(self.db.db_path).generar_rst_iva("2026-01-01", datetime.now().strftime("%Y-%m-%d"))
        Toast(self.app.main_window, f"PDF generado: {filename}", "success").show()