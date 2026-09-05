"""Pantalla principal operativa del inventario."""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime, timedelta
from ..styles import COLORS
from ..widgets import Card, DataTable, Toast


class DashboardView:
    """Resumen diario con accesos directos a los flujos de trabajo."""

    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.fecha_desde = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
        self.fecha_hasta = datetime.now().strftime("%Y-%m-%d")
        self.main_box = None
        self.resumen_box = None
        self.fondos_card = None

    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=15, background_color=COLORS['background']))
        header = toga.Box(style=Pack(direction=ROW, gap=10))
        header.add(toga.Label("INVENTARIO", style=Pack(font_size=26, font_weight="bold", color=COLORS['primary'])))
        header.add(toga.Box(style=Pack(flex=1)))
        header.add(toga.Label(f"Usuario: {getattr(self.app, 'user', 'Administrador')}", style=Pack(color=COLORS['gray_600'], margin=8)))
        self.main_box.add(header)

        self.resumen_box = toga.Box(style=Pack(direction=ROW, gap=12))
        self._actualizar_tarjetas()
        self.main_box.add(self.resumen_box)

        chart_card = Card(toga.Box(style=Pack(direction=COLUMN, gap=8)), margin=15, bgcolor="transparent")
        chart_card.add(toga.Label("Tendencia de ventas · últimos 7 días", style=Pack(font_size=17, font_weight="bold", color=COLORS['white'])))
        chart = toga.Box(style=Pack(direction=ROW, gap=10, margin_top=12, height=145))
        hoy = datetime.now()
        tendencia = self.db.obtener_dashboard()['tendencia']
        valores = [tendencia.get((hoy - timedelta(days=6 - i)).strftime('%Y-%m-%d'), 0) for i in range(7)]
        maximo = max(valores or [1]) or 1
        for i, value in enumerate(valores):
            day = (hoy - timedelta(days=6 - i)).strftime('%a')[:3].title()
            column = toga.Box(style=Pack(direction=COLUMN, flex=1, align_items="end", gap=4))
            column.add(toga.Label(f"${value:,.0f}", style=Pack(font_size=10, text_align="center")))
            column.add(toga.Box(style=Pack(height=max(10, int(value / maximo * 100)), background_color=COLORS['primary'])))
            column.add(toga.Label(day, style=Pack(font_size=11, text_align="center")))
            chart.add(column)
        chart_card.add(chart)
        self.main_box.add(chart_card)

        self.main_box.add(toga.Label("Acciones rápidas", style=Pack(font_size=17, font_weight="bold", margin_top=5, color="white")))
        actions = toga.Box(style=Pack(direction=ROW, gap=10))
        for label, shortcut, handler, color in [
            ("NUEVA VENTA", "F12", self._nueva_venta, COLORS['success']),
            ("ENTRADA MERCANCÍA", "", self.app.show_inventario, COLORS['info']),
            ("AJUSTE STOCK", "", self.app.show_inventario, COLORS['warning']),
            ("INVENTARIO FÍSICO", "", self.app.show_inventario, COLORS['primary']),
        ]:
            text = f"{label}\n({shortcut})" if shortcut else label
            actions.add(toga.Button(text, on_press=handler, style=Pack(flex=1, margin=14, background_color=color, color=COLORS['white'], font_weight="bold")))
        self.main_box.add(actions)

        asientos = self.db.obtener_ultimos_asientos(6)
        # Encabezado
        header = toga.Box(style=Pack(direction=ROW, background_color="#333333"))
        for title in ["Fecha", "Descripción", "Cuenta", "Valor"]:
            header.add(toga.Label(title, style=Pack(flex=1, color=COLORS['white'], font_weight="bold", margin=5)))
        self.main_box.add(header)

        # Filas
        for a in asientos:
            row = toga.Box(style=Pack(direction=ROW, background_color="#222222"))
            row.add(toga.Label(a['fecha'][:10], style=Pack(flex=1, color=COLORS['white'], margin=5)))
            row.add(toga.Label(a['descripcion'][:28], style=Pack(flex=1, color=COLORS['white'], margin=5)))
            row.add(toga.Label(a['nombre_cuenta'], style=Pack(flex=1, color=COLORS['white'], margin=5)))
            row.add(toga.Label(f"${max(a['debito'], a['credito']):,.0f}", style=Pack(flex=1, color=COLORS['white'], margin=5)))
            self.main_box.add(row)

        return self.main_box

    def _actualizar_tarjetas(self):
        self.resumen_box.clear()
        resumen = self.db.obtener_dashboard()
        margen_pct = (resumen['margen_bruto'] / resumen['ventas'] * 100) if resumen['ventas'] else 0
        cumplimiento = resumen['cumplimiento']
        tarjetas = [
            ("Ventas Totales", f"${resumen['ventas']:,.0f}", COLORS['primary']),
            ("CMV", f"${resumen['cmv']:,.0f}", COLORS['warning']),
            ("Margen Bruto", f"${resumen['margen_bruto']:,.0f} ({margen_pct:.1f}%)", COLORS['success']),
            ("Meta del Día", f"${resumen['meta']:,.0f} · {cumplimiento:.1f}%", COLORS['info']),
        ]
        for title, value, color in tarjetas:
            card = Card(toga.Box(style=Pack(direction=COLUMN, gap=5)), margin=14, bgcolor="transparent")
            card.add(toga.Label(title, style=Pack(font_size=12, color=COLORS['gray_600'])))
            card.add(toga.Label(value, style=Pack(font_size=20, font_weight="bold", color=color)))
            self.resumen_box.add(card)

        if self.fondos_card:
            self.main_box.remove(self.fondos_card)
        fondos = Card(toga.Box(style=Pack(direction=COLUMN, gap=6)), margin=14, bgcolor="transparent")
        fondos.add(toga.Label("Fondos por método de pago", style=Pack(font_size=16, font_weight="bold", color="white")))
        for metodo, total in resumen['fondos'].items():
            fondos.add(toga.Label(f"{metodo}: ${total:,.0f}", style=Pack(color=COLORS['text_secondary'])))
        self.fondos_card = fondos       
        self.main_box.add(fondos)

    def _nueva_venta(self, _widget):
        self.app.show_ventas()

    def actualizar_dashboard(self, _widget):
        self._actualizar_tarjetas()
        Toast(self.app.main_window, "Dashboard actualizado", "success").show()