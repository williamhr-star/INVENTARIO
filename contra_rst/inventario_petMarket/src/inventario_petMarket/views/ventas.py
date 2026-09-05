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
        self.pagos_box = None
        self._pago_controles = []
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=12))
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("PUNTO DE VENTA", style=Pack(font_size=24, font_weight="bold", color=COLORS['primary']))
        )
        header.add(toga.Box(style=Pack(flex=1)))
        header.add(toga.Label("F12 · Nueva venta", style=Pack(color=COLORS['gray_600'], margin=8)))
        self.main_box.add(header)
        self.busqueda_input = toga.TextInput(style=Pack(flex=1, margin=10))
        self.busqueda_input.hint_text = "Escanear código de barras o buscar producto"
        self.busqueda_input.on_change = self._mostrar_productos
        self.cantidad_input = toga.NumberInput(value=1, min=1, style=Pack(width=90))
        buscar = toga.Box(style=Pack(direction=ROW, gap=10))
        buscar.add(self.busqueda_input, toga.Label("Cantidad", style=Pack(margin=10)), self.cantidad_input)
        self.main_box.add(buscar)

        self.productos_box = toga.Box(style=Pack(direction=COLUMN, gap=5))
        self.carrito_box = toga.Box(style=Pack(direction=COLUMN, gap=5))
        self.productos = self.db.obtener_productos()
        self._mostrar_productos(None)
        left = Card(self.productos_box, margin=12)
        right_content = toga.Box(style=Pack(direction=COLUMN, gap=8))
        right_content.add(toga.Label("Detalle de venta", style=Pack(font_size=17, font_weight="bold")), self.carrito_box)
        self.total_label = toga.Label("Total a pagar: $0", style=Pack(font_size=22, font_weight="bold", color=COLORS['primary'], margin_top=12))
        right_content.add(self.total_label, toga.Label("División de pagos", style=Pack(font_weight="bold")))
        self.pagos_box = toga.Box(style=Pack(direction=COLUMN, gap=8))
        right_content.add(self.pagos_box)
        self._agregar_pago(None)
        right_content.add(toga.Button("+ Agregar método", on_press=self._agregar_pago, style=Pack(margin=10, color=COLORS['primary'])))
        buttons = toga.Box(style=Pack(direction=ROW, gap=8))
        buttons.add(ActionButton("COBRAR", self._cobrar, "✓", COLORS['success'], flex=1))
        buttons.add(ActionButton("CANCELAR", self._cancelar, "×", COLORS['danger'], flex=1))
        right_content.add(buttons)
        right = Card(right_content, margin=12)
        body = toga.Box(style=Pack(direction=ROW, flex=1, gap=15))
        body.add(left, right)
        self.main_box.add(body)
        return self.main_box

    def _mostrar_productos(self, _widget):
        self.productos_box.clear()
        termino = (self.busqueda_input.value or '').lower() if self.busqueda_input else ''
        encontrados = [p for p in self.productos if termino in f"{p['codigo']} {p['nombre']}".lower()][:8]
        for producto in encontrados:
            boton = toga.Button(f"{producto['codigo']} · {producto['nombre']}  |  ${producto['precio_venta']:,.0f}  |  Stock {producto['stock_actual']:.0f}", on_press=lambda w, p=producto: self._agregar(p), style=Pack(margin=12, text_align="left", background_color=COLORS['gray_100'], color=COLORS['text_primary']))
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
            fila = toga.Box(style=Pack(direction=ROW, gap=8, margin=5))
            fila.add(toga.Label(f"{item['nombre']}", style=Pack(flex=1)))
            fila.add(toga.Label(f"{item['cantidad']:.0f} x ${item['precio_unitario']:,.0f} = ${subtotal:,.0f}"))
            fila.add(toga.Button("Eliminar", on_press=lambda w, i=item: self._eliminar(i), style=Pack(margin=8, color=COLORS['danger'])))
            self.carrito_box.add(fila)
        self.total_label.text = f"TOTAL A PAGAR: ${total:,.0f}"

    def _cobrar(self, _widget):
        if not self.carrito:
            Toast(self.app.main_window, "Agrega al menos un producto", "warning").show()
            return
        total = sum(i['cantidad'] * i['precio_unitario'] for i in self.carrito)
        detalles = [{'producto_id': i['producto_id'], 'cantidad': i['cantidad'], 'precio_unitario': i['precio_unitario'], 'subtotal': i['cantidad'] * i['precio_unitario']} for i in self.carrito]
        pagos = []
        for metodo, monto_input, _ in getattr(self, '_pago_controles', []):
            monto = float(monto_input.value or 0)
            if monto > 0:
                pagos.append({'metodo': metodo.value, 'monto': monto})
        if round(sum(p['monto'] for p in pagos), 2) != round(total, 2):
            Toast(self.app.main_window, "Los pagos deben cubrir exactamente el total", "warning").show()
            return
        venta_id = self.db.registrar_venta({'subtotal': total, 'total': total, 'usuario': getattr(self.app, 'user', 'Administrador')}, detalles, pagos)
        Toast(self.app.main_window, f"Venta #{venta_id} registrada", "success").show()
        self._cancelar(None)

    def _cancelar(self, _widget):
        self.carrito = []
        self._pago_controles = []
        if self.pagos_box:
            self.pagos_box.clear()
            self._agregar_pago(None)
        self._actualizar_carrito()

    def _eliminar(self, item):
        self.carrito.remove(item)
        self._actualizar_carrito()

    def _agregar_pago(self, _widget):
        if not self.pagos_box:
            return
        metodo = toga.Selection(items=["Efectivo", "Tarjeta", "Nequi", "Daviplata", "Otro"], value="Efectivo", style=Pack(flex=1))
        monto = toga.NumberInput(min=0, style=Pack(width=130, margin=8))
        vuelto = toga.Label("Vuelto: $0", style=Pack(width=110, color=COLORS['success']))
        fila = toga.Box(style=Pack(direction=ROW, gap=8))
        fila.add(metodo, monto, vuelto)
        self.pagos_box.add(fila)
        self._pago_controles.append((metodo, monto, vuelto))
        def actualizar(_change):
            total = sum(i['cantidad'] * i['precio_unitario'] for i in self.carrito)
            vuelto.text = f"Vuelto: ${max(0, float(monto.value or 0) - total):,.0f}" if metodo.value == "Efectivo" else ""
        monto.on_change = actualizar
        metodo.on_change = actualizar