"""
Widgets reutilizables para toda la aplicación
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from .styles import COLORS


class Card(toga.Box):
    """Tarjeta con borde redondeado"""
    def __init__(self, content, padding=15, bgcolor=COLORS['white'], **kwargs):
        super().__init__(
            style=Pack(
                direction=COLUMN,
                margin=padding,
                background_color=bgcolor,
                **kwargs
            )
        )
        self.add(content)
        # Simular sombra con borde
        self.style.border_color = COLORS['gray_200']
        self.style.border_width = 1
        self.style.border_radius = 10


class StatCard(toga.Box):
    """Tarjeta de estadísticas (Ingresos, Gastos, etc)"""
    def __init__(self, title, value, color=COLORS['primary'], icon="📊"):
        super().__init__(
            style=Pack(
                direction=COLUMN,
                padding=20,
                background_color=color,
                width=200,
                flex=False
            )
        )
        self.add(
            toga.Label(f"{icon} {title}", 
                    style=Pack(color=COLORS['white'], font_size=12, font_weight="bold"))
        )
        self.add(
            toga.Label(str(value), 
                    style=Pack(color=COLORS['white'], font_size=24, font_weight="bold"))
        )


class DataTable(toga.Box):
    """Tabla de datos con encabezado y filas"""
    def __init__(self, columns, data, _row_actions=None):
        super().__init__(style=Pack(direction=COLUMN, background_color=COLORS['white'], margin=5))
        
        # Calcular ancho de columnas
        col_width = int(800 / len(columns)) if len(columns) > 0 else 100
        
        # Encabezado
        header = toga.Box(
            style=Pack(
                direction=ROW,
                margin=8,
                background_color=COLORS['gray_200'],
            )
        )
        for col in columns:
            header.add(
                toga.Label(col, style=Pack(width=col_width, font_weight="bold", font_size=12))
            )
        self.add(header)
        
        # Datos
        if not data:
            self.add(
                toga.Label("Sin datos disponibles", 
                        style=Pack(margin=20, color=COLORS['gray_600']))
            )
        else:
            for row_data in data:
                row = toga.Box(
                    style=Pack(
                        direction=ROW,
                        margin=6,
                    )
                )
                
                if isinstance(row_data, dict):
                    values = list(row_data.values())
                else:
                    values = row_data
                
                for value in values[:len(columns)]:
                    row.add(
                        toga.Label(str(value), style=Pack(width=col_width, font_size=11))
                    )
                
                self.add(row)


class ActionButton(toga.Button):
    """Botón de acción con estilo consistente"""
    def __init__(self, label, on_press, icon=None, color=COLORS['primary'], **kwargs):
        label_with_icon = f"{icon} {label}" if icon else label
        super().__init__(
            label_with_icon,
            on_press=on_press,
            style=Pack(
                background_color=color,
                color=COLORS['white'],
                padding=10,
                font_size=13,
                **kwargs
            )
        )


class SearchBar(toga.Box):
    """Barra de búsqueda con filtro"""
    def __init__(self, on_search, placeholder="Buscar..."):
        super().__init__(style=Pack(direction=ROW, gap=10, padding=10))
        
        self.search_input = toga.TextInput(style=Pack(flex=1, padding=8))
        self.search_input.hint_text = placeholder
        self.search_input.on_change = on_search
        
        self.add(self.search_input)
        self.add(
            toga.Button(
                "🔍 Buscar",
                on_press=on_search,
                style=Pack(background_color=COLORS['primary'], color=COLORS['white'])
            )
        )


class Toast(toga.Window):
    """Mensaje emergente (notificación)"""
    def __init__(self, parent, message, notification_type="info"):
        bgcolor = {
            'success': COLORS['success'],
            'error': COLORS['danger'],
            'warning': COLORS['warning'],
            'info': COLORS['primary']
        }.get(notification_type, COLORS['info'])
        
        super().__init__(title="", size=(400, 80), resizable=False, closable=False)
        self.parent = parent
        
        box = toga.Box(style=Pack(direction=COLUMN, padding=20, background_color=bgcolor))
        box.add(
            toga.Label(message, 
                    style=Pack(color=COLORS['white'], font_size=14))
        )
        self.content = box
    
    def show(self):
        super().show()
        import threading
        threading.Timer(3.0, self.close).start()


class ModalDialog(toga.Window):
    """Ventana modal para formularios"""
    def __init__(self, parent, title, content, on_confirm, on_cancel=None, width=500, height=400):
        super().__init__(title=title, size=(width, height))
        self.parent = parent
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel or self.close
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, gap=15, flex=1))
        
        # Contenido
        if isinstance(content, toga.Box):
            main_box.add(content)
        else:
            main_box.add(content)
        
        # Botones
        buttons = toga.Box(style=Pack(direction=ROW, gap=10, margin_top=20))
        buttons.add(
            toga.Button("Cancelar", on_press=self.on_cancel,
                    style=Pack(background_color=COLORS['gray_500'], color=COLORS['white']))
        )
        buttons.add(
            toga.Button("Guardar", on_press=self.on_confirm,
                    style=Pack(background_color=COLORS['success'], color=COLORS['white']))
        )
        main_box.add(buttons)
        
        self.content = main_box