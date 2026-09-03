"""
Vista de ventas con comparación de costos
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..styles import COLORS
from ..widgets import Card, ActionButton, Toast, ModalDialog


class VentasView:
    """Vista de gestión de ventas"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.producto_seleccionado = None
        self.main_box = None
        
        # Inicializar atributos antes de usarlos
        self.producto_dropdown = None
        self.producto_map = {}
        self.info_box = None
        self.cantidad_input = None
        self.precio_input = None  # ✅ DEFINIDO AQUÍ
        self.comparacion_box = None
        self.comparacion_label = None
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=15))
        
        # ========== ENCABEZADO ==========
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("💰 REGISTRAR VENTA", 
                      style=Pack(font_size=24, font_weight="bold", color=COLORS['success']))
        )
        self.main_box.add(header)
        
        # ========== SELECCIONAR PRODUCTO ==========
        productos = self.db.obtener_productos()
        options = [(str(p['id']), f"{p['codigo']} - {p['nombre']} (Stock: {p['stock_actual']})") for p in productos]
        
        self.producto_dropdown = toga.Selection(
            items=[opt[1] for opt in options],
            style=Pack(width=400, margin=10)
        )
        self.producto_dropdown.on_select = self._cargar_producto
        self.producto_map = {opt[1]: int(opt[0]) for opt in options}
        
        self.main_box.add(
            toga.Box(style=Pack(direction=COLUMN, gap=5), children=[
                toga.Label("Seleccionar Producto:", style=Pack(font_weight="bold")),
                self.producto_dropdown
            ])
        )
        
        # ========== INFORMACIÓN DEL PRODUCTO ==========
        self.info_box = Card(
            toga.Box(style=Pack(direction=COLUMN, gap=5)),
            padding=15,
            bgcolor=COLORS['gray_50']
        )
        self._actualizar_info_producto(None)
        self.main_box.add(self.info_box)
        
        # ========== CAMPOS DE VENTA ==========
        form = toga.Box(style=Pack(direction=COLUMN, gap=10))
        
        cantidad_label = toga.Label("Cantidad:", style=Pack(font_weight="bold"))
        self.cantidad_input = toga.NumberInput(min=0, style=Pack(width=150))
        self.cantidad_input.hint_text = "0"  # ✅ Usar hint_text en lugar de placeholder
        
        precio_label = toga.Label("Precio de venta unitario:", style=Pack(font_weight="bold"))
        self.precio_input = toga.NumberInput(min=0, style=Pack(width=150))  # ✅ DEFINIDO
        self.precio_input.hint_text = "0"  # ✅ Usar hint_text
        
        self.comparacion_box = Card(
            toga.Box(style=Pack(direction=COLUMN, gap=5)),
            padding=15,
            bgcolor=COLORS['primary_light']
        )
        self.comparacion_label = toga.Label("Ingrese cantidad y precio para calcular", 
                                            style=Pack(color=COLORS['gray_600']))
        self.comparacion_box.add(self.comparacion_label)
        
        form.add(
            cantidad_label, self.cantidad_input,
            precio_label, self.precio_input,
            toga.Button("Calcular", on_press=self._calcular_comparacion,
                       style=Pack(background_color=COLORS['info'], color=COLORS['white'], width=150)),
            self.comparacion_box,
            ActionButton("✅ REGISTRAR VENTA", self._registrar_venta, "💰", COLORS['success'])
        )
        
        self.main_box.add(form)
        
        # ========== ÚLTIMAS VENTAS ==========
        self.main_box.add(
            toga.Label("📋 ÚLTIMAS VENTAS", 
                      style=Pack(font_size=18, font_weight="bold", margin_top=20))
        )
        self._actualizar_ultimas_ventas()
        
        return self.main_box
    
    def _cargar_producto(self, widget):
        """Carga la información del producto seleccionado"""
        self._actualizar_info_producto(widget)
    
    def _actualizar_info_producto(self, _widget):
        """Actualiza la información del producto"""
        self.info_box.clear()
        
        if not self.producto_dropdown or not self.producto_dropdown.value:
            self.info_box.add(toga.Label("Seleccione un producto", style=Pack(color=COLORS['gray_600'])))
            return
        
        producto_id = self.producto_map.get(self.producto_dropdown.value)
        if not producto_id:
            return
        
        producto = self.db.obtener_producto(producto_id)
        if not producto:
            return
        
        self.producto_seleccionado = producto
        
        info = toga.Box(style=Pack(direction=COLUMN, gap=5))
        info.add(
            toga.Label(f"📦 {producto['nombre']}", style=Pack(font_size=16, font_weight="bold")),
            toga.Label(f"Stock disponible: {producto['stock_actual']} {producto.get('unidad_medida', 'unidades')}"),
            toga.Label(f"Costo unitario: ${producto['precio_costo']:,.0f}"),
            toga.Label(f"Precio venta sugerido: ${producto['precio_venta']:,.0f}"),
        )
        self.info_box.add(info)
        
        # Pre-cargar precio de venta
        if self.precio_input:
            self.precio_input.value = producto['precio_venta']
    
    def _calcular_comparacion(self, _widget):
        """Calcula y muestra la comparación de costos vs venta"""
        if not self.producto_seleccionado:
            Toast(self.app.main_window, "⚠️ Seleccione un producto primero", "warning").show()
            return
        
        cantidad = float(self.cantidad_input.value or 0)
        precio_venta = float(self.precio_input.value or 0)
        
        if cantidad <= 0 or precio_venta <= 0:
            Toast(self.app.main_window, "⚠️ Ingrese cantidad y precio válidos", "warning").show()
            return
        
        if cantidad > self.producto_seleccionado['stock_actual']:
            Toast(self.app.main_window, "❌ Stock insuficiente", "error").show()
            return
        
        costo_unitario = self.producto_seleccionado['precio_costo']
        costo_total = costo_unitario * cantidad
        venta_total = precio_venta * cantidad
        ganancia = venta_total - costo_total
        margen = (ganancia / venta_total) * 100 if venta_total > 0 else 0
        
        # Actualizar comparación
        self.comparacion_box.clear()
        
        comparacion = toga.Box(style=Pack(direction=COLUMN, gap=5))
        comparacion.add(
            toga.Label("📊 ANÁLISIS DE RENTABILIDAD", 
                      style=Pack(font_weight="bold", color=COLORS['primary']))
        )
        comparacion.add(
            toga.Label(f"💸 Costo total: ${costo_total:,.0f} ({costo_unitario:,.0f} x {cantidad})")
        )
        comparacion.add(
            toga.Label(f"💵 Venta total: ${venta_total:,.0f} ({precio_venta:,.0f} x {cantidad})")
        )
        
        ganancia_color = COLORS['success'] if ganancia >= 0 else COLORS['danger']
        comparacion.add(
            toga.Label(
                f"💰 Ganancia: ${ganancia:,.0f} ({margen:.1f}% de margen)",
                style=Pack(color=ganancia_color, font_weight="bold")
            )
        )
        
        self.comparacion_box.add(comparacion)
    
    def _registrar_venta(self, _widget):
        """Registra la venta"""
        if not self.producto_seleccionado:
            Toast(self.app.main_window, "⚠️ Seleccione un producto", "warning").show()
            return
        
        cantidad = float(self.cantidad_input.value or 0)
        precio_venta = float(self.precio_input.value or 0)
        
        if cantidad <= 0 or precio_venta <= 0:
            Toast(self.app.main_window, "⚠️ Ingrese cantidad y precio válidos", "warning").show()
            return
        
        if cantidad > self.producto_seleccionado['stock_actual']:
            Toast(self.app.main_window, "❌ Stock insuficiente", "error").show()
            return
        
        # Confirmar venta
        def confirmar(_widget):
            datos_venta = {
                'cliente': 'Cliente General',
                'tipo_comprobante': 'Boleta',
                'subtotal': precio_venta * cantidad,
                'total': precio_venta * cantidad,
                'usuario': 'Admin'
            }
            
            detalles = [{
                'producto_id': self.producto_seleccionado['id'],
                'cantidad': cantidad,
                'precio_unitario': precio_venta,
                'subtotal': precio_venta * cantidad
            }]
            
            venta_id = self.db.registrar_venta(datos_venta, detalles)
            Toast(self.app.main_window, f"✅ Venta #{venta_id} registrada!", "success").show()
            
            # Limpiar campos
            self.cantidad_input.value = 0
            self.comparacion_box.clear()
            self.comparacion_box.add(toga.Label("", style=Pack(color=COLORS['gray_600'])))
            
            # Actualizar información del producto
            self._actualizar_info_producto(None)
            dialog.close()
        
        dialog = ModalDialog(
            self.app.main_window,
            "Confirmar Venta",
            toga.Label("¿Confirmar esta venta?"),
            confirmar
        )
        dialog.show()
    
    def _actualizar_ultimas_ventas(self):
        """Actualiza la lista de últimas ventas"""
        pass