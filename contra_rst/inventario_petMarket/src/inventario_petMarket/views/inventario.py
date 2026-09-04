"""
Vista de inventario con control de stock
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..styles import COLORS
from ..widgets import Card, StatCard, ActionButton, Toast


class InventarioView:
    """Vista de gestión de inventario"""
    
    def __init__(self, app, db_manager):
        self.app = app
        self.db = db_manager
        self.productos = []
        self.main_box = None
        self.tabla_box = None
        self.busqueda_input = None
        self.stock_bajo_check = None
    
    def build(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, gap=15))
        
        # ========== ENCABEZADO ==========
        header = toga.Box(style=Pack(direction=ROW, flex=False, gap=10))
        header.add(
            toga.Label("📦 INVENTARIO", 
                      style=Pack(font_size=24, font_weight="bold", color=COLORS['primary']))
        )
        header.add(
            ActionButton("Nuevo Producto", self._nuevo_producto, "➕", COLORS['success'])
        )
        header.add(
            ActionButton("Actualizar", self._actualizar_lista, "🔄", COLORS['primary'])
        )
        self.main_box.add(header)
        
        # ========== RESUMEN RÁPIDO ==========
        resumen = self._obtener_resumen()
        cards = [
            StatCard("Total Productos", resumen['total'], COLORS['primary'], "📦"),
            StatCard("Stock Bajo", resumen['stock_bajo'], COLORS['danger'], "⚠️"),
            StatCard("Valor Inventario", f"${resumen['valor_total']:,.0f}", COLORS['success'], "💰"),
        ]
        self.main_box.add(toga.Box(style=Pack(direction=ROW, gap=20), children=cards))

        filtros = toga.Box(style=Pack(direction=ROW, gap=10))
        self.busqueda_input = toga.TextInput(style=Pack(flex=1, padding=8))
        self.busqueda_input.hint_text = "Buscar por código, nombre o categoría"
        self.busqueda_input.on_change = self._filtrar_productos
        self.stock_bajo_check = toga.Switch("Solo stock bajo", on_change=self._filtrar_productos)
        filtros.add(self.busqueda_input, self.stock_bajo_check)
        self.main_box.add(filtros)
        
        # ========== TABLA DE PRODUCTOS ==========
        self.tabla_box = toga.Box(style=Pack(direction=COLUMN))
        self._actualizar_lista(None)
        
        # ✅ ScrollContainer corregido
        scroll = toga.ScrollContainer()
        scroll.content = self.tabla_box
        scroll.style.flex = 1
        self.main_box.add(scroll)
        
        return self.main_box
    
    def _obtener_resumen(self):
        productos = self.db.obtener_productos()
        total = len(productos)
        stock_bajo = sum(1 for p in productos if p['stock_actual'] < p['stock_minimo'])
        valor_total = sum(p['stock_actual'] * p['precio_costo'] for p in productos)
        return {'total': total, 'stock_bajo': stock_bajo, 'valor_total': valor_total}
    
    def _filtrar_productos(self, _widget):
        self._actualizar_lista(None)

    def _actualizar_lista(self, _widget):
        """Actualiza la tabla de productos"""
        self.tabla_box.clear()
        
        productos = self.db.obtener_productos(bool(self.stock_bajo_check and self.stock_bajo_check.value))
        termino = (self.busqueda_input.value or '').strip().lower() if self.busqueda_input else ''
        if termino:
            productos = [p for p in productos if termino in ' '.join([
                str(p.get('codigo', '')), str(p.get('nombre', '')), str(p.get('categoria', ''))
            ]).lower()]
        self.productos = productos
        
        if not productos:
            self.tabla_box.add(
                toga.Label("No hay productos registrados", 
                          style=Pack(padding=40, color=COLORS['gray_600'], text_align="center"))
            )
            return
        
        # Encabezado
        header = toga.Box(style=Pack(direction=ROW, padding=8, background_color=COLORS['gray_200']))
        for titulo in ["Código", "Nombre", "Categoría", "Stock actual", "Precio", "Estado"]:
            header.add(toga.Label(titulo, style=Pack(width=115, font_weight="bold")))
        self.tabla_box.add(header)
        
        # Filas
        for p in productos:
            row = toga.Box(
                style=Pack(
                    direction=ROW,
                    padding=6,
                    background_color=COLORS['danger_light'] if p['stock_actual'] <= p['stock_minimo'] else COLORS['gray_50']
                )
            )
            estado = "Agotado" if p['stock_actual'] <= 0 else "Stock bajo" if p['stock_actual'] <= p['stock_minimo'] else "Disponible"
            estado_color = COLORS['danger'] if estado != "Disponible" else COLORS['success']
            row.add(
                toga.Label(p['codigo'], style=Pack(width=115)),
                toga.Label(p['nombre'][:24], style=Pack(width=115)),
                toga.Label(p.get('categoria', '')[:16], style=Pack(width=115)),
                toga.Label(f"{p['stock_actual']:.2f}", style=Pack(width=115)),
                toga.Label(f"${p['precio_venta']:,.0f}", style=Pack(width=115)),
                toga.Label(estado, style=Pack(width=115, color=estado_color, font_weight="bold")),
            )
            self.tabla_box.add(row)
        
    
    def _nuevo_producto(self, _widget):
        """Abre diálogo para crear nuevo producto"""
        # Crear formulario
        form = toga.Box(style=Pack(direction=COLUMN, gap=10))
        
        codigo_input = toga.TextInput(style=Pack(width=300))
        codigo_input.hint_text = "Código (ej: PROD-001)"
        
        nombre_input = toga.TextInput(style=Pack(width=300))
        nombre_input.hint_text = "Nombre del producto"
        
        categoria_input = toga.TextInput(style=Pack(width=300))
        categoria_input.hint_text = "Categoría"
        
        costo_input = toga.NumberInput(min=0, style=Pack(width=150))
        costo_input.hint_text = "Precio Costo"
        
        venta_input = toga.NumberInput(min=0, style=Pack(width=150))
        venta_input.hint_text = "Precio Venta"
        
        stock_input = toga.NumberInput(min=0, style=Pack(width=150))
        stock_input.hint_text = "Stock Inicial"
        
        min_input = toga.NumberInput(min=0, style=Pack(width=150))
        min_input.hint_text = "Stock Mínimo"
        
        form.add(
            toga.Label("Nuevo Producto", style=Pack(font_size=18, font_weight="bold")),
            codigo_input, nombre_input, categoria_input,
            costo_input, venta_input, stock_input, min_input
        )
        
        def confirmar(_widget):
            datos = {
                'codigo': codigo_input.value,
                'nombre': nombre_input.value,
                'categoria': categoria_input.value,
                'precio_costo': float(costo_input.value or 0),
                'precio_venta': float(venta_input.value or 0),
                'stock_actual': float(stock_input.value or 0),
                'stock_minimo': float(min_input.value or 0)
            }
            self.db.crear_producto(datos)
            self._actualizar_lista(None)
            Toast(self.app.main_window, "✅ Producto creado exitosamente", "success").show()
            dialog.close()
        
        # Ventana modal simple
        dialog = toga.Window(title="Nuevo Producto", size=(500, 500))
        content = toga.Box(style=Pack(direction=COLUMN, padding=20, gap=10))
        content.add(form)
        
        buttons = toga.Box(style=Pack(direction=ROW, gap=10, margin_top=20))
        buttons.add(
            toga.Button("Cancelar", on_press=lambda w: dialog.close(),
                       style=Pack(background_color=COLORS['gray_500'], color=COLORS['white']))
        )
        buttons.add(
            toga.Button("Guardar", on_press=confirmar,
                       style=Pack(background_color=COLORS['success'], color=COLORS['white']))
        )
        content.add(buttons)
        
        dialog.content = content
        dialog.show()