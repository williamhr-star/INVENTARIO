import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime
from .styles import COLORS
from .pdf_generator import PDFGenerator

class DashboardView:
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.fecha_desde = "2026-01-01"
        self.fecha_hasta = datetime.now().strftime("%Y-%m-%d")
        
    def build(self):
        # Contenedor principal
        box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=20))
        
        # Encabezado
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("Resumen del período", 
                      style=Pack(font_size=24, font_weight="bold", color=COLORS['text_primary']))
        )
        
        # Botones de acción
        actions = toga.Box(style=Pack(direction=ROW, gap=10))
        actions.add(
            toga.Button(
                "📄 Generar PDF",
                on_press=self.generar_pdf,
                style=Pack(background_color=COLORS['danger'], color="white", padding=10)
            ),
            toga.Button(
                "➕ Asiento",
                on_press=self.crear_asiento,
                style=Pack(background_color=COLORS['primary'], color="white", padding=10)
            )
        )
        header.add(actions)
        box.add(header)
        
        # Selector de período
        period_box = toga.Box(style=Pack(direction=ROW, gap=10, padding=10, background_color=COLORS['white']))
        period_box.add(
            toga.Label("Período:", style=Pack(font_weight="bold")),
            toga.TextInput(value=self.fecha_desde, style=Pack(width=120), on_change=self.cambiar_desde),
            toga.Label("→", style=Pack(padding=5)),
            toga.TextInput(value=self.fecha_hasta, style=Pack(width=120), on_change=self.cambiar_hasta),
            toga.Button("Actualizar", on_press=self.actualizar, style=Pack(background_color=COLORS['primary'], color="white"))
        )
        box.add(period_box)
        
        # Tarjetas de resumen
        self.resumen_box = toga.Box(style=Pack(direction=ROW, gap=20, padding=10))
        self.actualizar_tarjetas()
        box.add(self.resumen_box)
        
        # Tabla de asientos
        box.add(toga.Label("Últimos asientos registrados", style=Pack(font_size=18, font_weight="bold", margin_top=20)))
        self.tabla_asientos = self.crear_tabla_asientos()
        box.add(self.tabla_asientos)
        
        # Estado de cuentas clave
        box.add(toga.Label("Estado de cuentas clave", style=Pack(font_size=18, font_weight="bold", margin_top=20)))
        self.cuentas_box = toga.Box(style=Pack(direction=COLUMN, gap=5))
        self.actualizar_cuentas()
        box.add(self.cuentas_box)
        
        return box
    
    def actualizar_tarjetas(self):
        """Actualiza las tarjetas de resumen"""
        self.resumen_box.clear()
        
        resumen = self.db.obtener_resumen_periodo(self.fecha_desde, self.fecha_hasta)
        
        tarjetas = [
            ("Ingresos del período", f"${resumen['ingresos']:,.0f}", COLORS['success']),
            ("Gastos del período", f"${resumen['gastos']:,.0f}", COLORS['danger']),
            ("Utilidad neta", f"${resumen['utilidad_neta']:,.0f}", COLORS['primary']),
            ("RST estimado", f"${resumen['rst_estimado']:,.0f}", COLORS['warning']),
        ]
        
        for titulo, valor, color in tarjetas:
            card = toga.Box(
                style=Pack(
                    direction=COLUMN,
                    padding=20,
                    background_color=color,
                    width=200,
                    flex=False
                )
            )
            card.add(
                toga.Label(titulo, style=Pack(color="white", font_size=12)),
                toga.Label(valor, style=Pack(color="white", font_size=24, font_weight="bold"))
            )
            self.resumen_box.add(card)
    
    def crear_tabla_asientos(self):
        """Crea la tabla de últimos asientos"""
        table = toga.Box(style=Pack(direction=COLUMN, background_color=COLORS['white'], padding=10))
        
        # Encabezado
        header = toga.Box(style=Pack(direction=ROW, padding=5, background_color=COLORS['gray_200']))
        for titulo in ["Fecha", "Descripción", "Cuenta", "Débito", "Crédito"]:
            header.add(
                toga.Label(titulo, style=Pack(width=100 if titulo != "Descripción" else 200, font_weight="bold"))
            )
        table.add(header)
        
        # Obtener asientos
        asientos = self.db.obtener_ultimos_asientos(10)
        
        if not asientos:
            table.add(toga.Label("Sin movimientos aún.", style=Pack(padding=10, color=COLORS['gray_600'])))
        else:
            for asiento in asientos:
                row = toga.Box(style=Pack(direction=ROW, padding=5))
                row.add(
                    toga.Label(asiento['fecha'][:10], style=Pack(width=100)),
                    toga.Label(asiento['descripcion'][:30], style=Pack(width=200)),
                    toga.Label(f"{asiento['cuenta']} - {asiento['nombre_cuenta'][:20]}", style=Pack(width=150)),
                    toga.Label(f"${asiento['debito']:,.0f}" if asiento['debito'] > 0 else "", style=Pack(width=100)),
                    toga.Label(f"${asiento['credito']:,.0f}" if asiento['credito'] > 0 else "", style=Pack(width=100)),
                )
                table.add(row)
        
        return table
    
    def actualizar_cuentas(self):
        """Actualiza el estado de cuentas clave"""
        self.cuentas_box.clear()
        
        cuentas = self.db.obtener_cuentas_clave()
        
        for codigo, info in cuentas.items():
            row = toga.Box(style=Pack(direction=ROW, gap=10, padding=5))
            row.add(
                toga.Label(f"{codigo} - {info['nombre']}", style=Pack(width=200)),
                toga.Label(f"${info['saldo']:,.0f}", 
                          style=Pack(color=COLORS['success'] if info['saldo'] >= 0 else COLORS['danger']))
            )
            self.cuentas_box.add(row)
    
    def cambiar_desde(self, widget):
        self.fecha_desde = widget.value
    
    def cambiar_hasta(self, widget):
        self.fecha_hasta = widget.value
    
    def actualizar(self, widget):
        self.actualizar_tarjetas()
        self.tabla_asientos = self.crear_tabla_asientos()
        self.actualizar_cuentas()
    
    def generar_pdf(self, widget):
        """Genera el PDF de resumen"""
        pdf_gen = PDFGenerator(self.db.db_path)
        filename = pdf_gen.generar_estado_resultados(self.fecha_desde, self.fecha_hasta)
        self.app.main_window.info_dialog("PDF Generado", f"Archivo creado: {filename}")
    
    def crear_asiento(self, widget):
        """Abre el diálogo para crear un nuevo asiento"""
        # Implementación del diálogo de asiento
        self.app.show_libro_diario()