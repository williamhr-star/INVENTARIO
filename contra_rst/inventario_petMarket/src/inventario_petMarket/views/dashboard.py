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

    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=20, gap=15))
        header = toga.Box(style=Pack(direction=ROW, gap=10))
        header.add(toga.Label("INVENTARIO", style=Pack(font_size=26, font_weight="bold", color=COLORS['primary'])))
        header.add(toga.Box(style=Pack(flex=1)))
        header.add(toga.Label(f"Usuario: {getattr(self.app, 'user', 'Administrador')}", style=Pack(color=COLORS['gray_600'], margin=8)))
        self.main_box.add(header)

        self.resumen_box = toga.Box(style=Pack(direction=ROW, gap=12))
        self._actualizar_tarjetas()
        self.main_box.add(self.resumen_box)

        chart_card = Card(toga.Box(style=Pack(direction=COLUMN, gap=8)), padding=15)
        chart_card.add(toga.Label("Tendencia de ventas · últimos 7 días", style=Pack(font_size=17, font_weight="bold")))
        chart = toga.Box(style=Pack(direction=ROW, gap=10, margin_top=12, height=145))
        for day, value in zip(("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"), (52, 76, 44, 88, 64, 95, 70)):
            column = toga.Box(style=Pack(direction=COLUMN, flex=1, align_items="end", gap=4))
            column.add(toga.Label(f"{value}%", style=Pack(font_size=10, text_align="center")))
            column.add(toga.Box(style=Pack(height=max(10, value), background_color=COLORS['info'])))
            column.add(toga.Label(day, style=Pack(font_size=11, text_align="center")))
            chart.add(column)
        chart_card.add(chart)
        self.main_box.add(chart_card)

        self.main_box.add(toga.Label("Acciones rápidas", style=Pack(font_size=17, font_weight="bold", margin_top=5)))
        actions = toga.Box(style=Pack(direction=ROW, gap=10))
        for label, shortcut, handler, color in [
            ("NUEVA VENTA", "F12", self._nueva_venta, COLORS['success']),
            ("ENTRADA MERCANCÍA", "", self.app.show_inventario, COLORS['info']),
            ("AJUSTE STOCK", "", self.app.show_inventario, COLORS['warning']),
            ("INVENTARIO FÍSICO", "", self.app.show_inventario, COLORS['primary']),
        ]:
            text = f"{label}\n({shortcut})" if shortcut else label
            actions.add(toga.Button(text, on_press=handler, style=Pack(flex=1, padding=14, background_color=color, color=COLORS['white'], font_weight="bold")))
        self.main_box.add(actions)

        self.main_box.add(toga.Label("Últimos movimientos contables", style=Pack(font_size=17, font_weight="bold", margin_top=5)))
        asientos = self.db.obtener_ultimos_asientos(6)
        data = [{"Fecha": a['fecha'][:10], "Descripción": a['descripcion'][:28], "Cuenta": a['nombre_cuenta'], "Valor": f"${max(a['debito'], a['credito']):,.0f}"} for a in asientos]
        self.main_box.add(DataTable(["Fecha", "Descripción", "Cuenta", "Valor"], data))
        return self.main_box

    def _actualizar_tarjetas(self):
        self.resumen_box.clear()
        resumen = self.db.obtener_resumen_periodo(self.fecha_desde, self.fecha_hasta)
        productos = self.db.obtener_productos()
        criticos = sum(1 for p in productos if p['stock_actual'] <= p['stock_minimo'])
        tarjetas = [
            ("Ventas Hoy", f"${resumen['ingresos']:,.0f}", COLORS['primary']),
            ("Ganancia Bruta", f"${resumen['utilidad_neta']:,.0f}", COLORS['success']),
            ("Stock Crítico", f"{criticos} Items", COLORS['warning']),
            ("CxC Vencidas", "$0", COLORS['danger']),
        ]
        for title, value, color in tarjetas:
            card = Card(toga.Box(style=Pack(direction=COLUMN, gap=5)), padding=14)
            card.add(toga.Label(title, style=Pack(font_size=12, color=COLORS['gray_600'])))
            card.add(toga.Label(value, style=Pack(font_size=20, font_weight="bold", color=color)))
            self.resumen_box.add(card)

    def _nueva_venta(self, _widget):
        self.app.show_ventas()

    def actualizar_dashboard(self, _widget):
        self._actualizar_tarjetas()
        Toast(self.app.main_window, "Dashboard actualizado", "success").show()