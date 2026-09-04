"""Punto de venta: búsqueda rápida, carrito y cobro."""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..styles import COLORS
from ..widgets import Card, ActionButton, Toast


class VentasView:
    """Vista de gestión de ventas"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.producto_seleccionado = None
        self.main_box = None
        self.productos = []
        self.carrito = []
        self.busqueda_input = None
        self.cantidad_input = None
        self.productos_box = None
        self.carrito_box = None
        self.total_label = None
        self.pago = None
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=12))
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("PUNTO DE VENTA", style=Pack(font_size=24, font_weight="bold", color=COLORS['primary']))
        )
        header.add(toga.Box(style=Pack(flex=1)))
        header.add(toga.Label("F12 · Nueva venta", style=Pack(color=COLORS['gray_600'], padding=8)))
        self.main_box.add(header)
        self.busqueda_input = toga.TextInput(style=Pack(flex=1, padding=10))
        self.busqueda_input.hint_text = "Escanear código de barras o buscar producto"
        self.busqueda_input.on_change = self._mostrar_productos
        self.cantidad_input = toga.NumberInput(value=1, min=1, style=Pack(width=90))
        buscar = toga.Box(style=Pack(direction=ROW, gap=10))
        buscar.add(self.busqueda_input, toga.Label("Cantidad", style=Pack(padding=10)), self.cantidad_input)
        self.main_box.add(buscar)

        self.productos_box = toga.Box(style=Pack(direction=COLUMN, gap=5))
        self.carrito_box = toga.Box(style=Pack(direction=COLUMN, gap=5))
        self.productos = self.db.obtener_productos()
        self._mostrar_productos(None)
        left = Card(self.productos_box, padding=12)
        right_content = toga.Box(style=Pack(direction=COLUMN, gap=8))
        right_content.add(toga.Label("Detalle de venta", style=Pack(font_size=17, font_weight="bold")), self.carrito_box)
        self.total_label = toga.Label("Total a pagar: $0", style=Pack(font_size=22, font_weight="bold", color=COLORS['primary'], padding_top=12))
        self.pago = toga.Selection(items=["EFECTIVO", "TARJETA", "TRANSFERENCIA"], value="EFECTIVO")
        right_content.add(self.total_label, toga.Label("Método de pago", style=Pack(font_weight="bold")), self.pago)
        buttons = toga.Box(style=Pack(direction=ROW, gap=8))
        buttons.add(ActionButton("COBRAR", self._cobrar, "✓", COLORS['success'], flex=1))
        buttons.add(ActionButton("CANCELAR", self._cancelar, "×", COLORS['danger'], flex=1))
        right_content.add(buttons)
        right = Card(right_content, padding=12)
        body = toga.Box(style=Pack(direction=ROW, flex=1, gap=15))
        body.add(left, right)
        self.main_box.add(body)
        return self.main_box

    def _mostrar_productos(self, _widget):
        self.productos_box.clear()
        termino = (self.busqueda_input.value or '').lower() if self.busqueda_input else ''
        encontrados = [p for p in self.productos if termino in f"{p['codigo']} {p['nombre']}".lower()][:8]
        for producto in encontrados:
            boton = toga.Button(f"{producto['codigo']} · {producto['nombre']}  |  ${producto['precio_venta']:,.0f}  |  Stock {producto['stock_actual']:.0f}", on_press=lambda w, p=producto: self._agregar(p), style=Pack(padding=8, text_align="left", background_color=COLORS['gray_100'], color=COLORS['white']))
            self.productos_box.add(boton)

    def _agregar(self, producto):
        cantidad = float(self.cantidad_input.value or 1)
        if cantidad > producto['stock_actual']:
            Toast(self.app.main_window, "Stock insuficiente", "error").show()
            return
        for item in self.carrito:
            if item['producto_id'] == producto['id']:
                item['cantidad'] += cantidad
                break
        else:
            self.carrito.append({'producto_id': producto['id'], 'nombre': producto['nombre'], 'cantidad': cantidad, 'precio_unitario': producto['precio_venta']})
        self._actualizar_carrito()

    def _actualizar_carrito(self):
        self.carrito_box.clear()
        total = 0
        for item in self.carrito:
            subtotal = item['cantidad'] * item['precio_unitario']
            total += subtotal
            self.carrito_box.add(toga.Label(f"{item['nombre']} · {item['cantidad']:.0f} x ${item['precio_unitario']:,.0f} = ${subtotal:,.0f}"))
        self.total_label.text = f"TOTAL A PAGAR: ${total:,.0f}"

    def _cobrar(self, _widget):
        if not self.carrito:
            Toast(self.app.main_window, "Agrega al menos un producto", "warning").show()
            return
        total = sum(i['cantidad'] * i['precio_unitario'] for i in self.carrito)
        detalles = [{'producto_id': i['producto_id'], 'cantidad': i['cantidad'], 'precio_unitario': i['precio_unitario'], 'subtotal': i['cantidad'] * i['precio_unitario']} for i in self.carrito]
        venta_id = self.db.registrar_venta({'subtotal': total, 'total': total, 'usuario': getattr(self.app, 'user', 'Administrador')}, detalles)
        Toast(self.app.main_window, f"Venta #{venta_id} registrada", "success").show()
        self._cancelar(None)

    def _cancelar(self, _widget):
        self.carrito = []
        self._actualizar_carrito()