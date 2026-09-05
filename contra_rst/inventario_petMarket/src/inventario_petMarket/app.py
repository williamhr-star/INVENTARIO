import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import os
import sys
from pathlib import Path

# Importar módulos
from .database import DatabaseManager
from .sync_manager import OneDriveSyncManager
from .views.dashboard import DashboardView
from .views.inventario import InventarioView
from .views.ventas import VentasView
from .views.contabilidad import ContabilidadView
from .views.asientos import AsientosView
from .views.reportes import ReportesView
from .views.configuracion import ConfiguracionView
from .styles import COLORS, STYLES
from . import APP_NAME

class ContraRSTApp(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_path = None
        self.db_manager = None
        self.sync_manager = None
        self.current_view = None
        self.main_box = None
        self.user = "Administrador"
        self.business_name = APP_NAME
        
    def startup(self):
        """Inicializa la aplicación"""
        # Configurar la ventana principal
        self.main_window = toga.MainWindow(
            title="Inventario PetMarket",
            size=(1300, 800),
            resizable=True,
        )
        
        # Configurar la base de datos
        self.setup_database()
        
        # Crear el layout principal
        self.main_box = toga.Box(style=Pack(direction=ROW, flex=1, background_color=COLORS['app_background']))
        
        # Menú lateral
        sidebar = self.create_sidebar()
        self.main_box.add(sidebar)
        
        # Contenido principal (Dashboard por defecto)
        self.content_box = toga.Box(style=Pack(direction=COLUMN, flex=1, margin=20, background_color=COLORS['app_background']))
        self.main_box.add(self.content_box)
        
        # Cargar Dashboard
        self.show_dashboard()
        
        # Mostrar la ventana
        self.main_window.content = self.main_box
        self.main_window.show()
    
    def setup_database(self):
        """Configura la base de datos y la sincronización con OneDrive"""
        # Ruta de la base de datos local
        app_dir = os.path.expanduser("~/ContraRST")
        os.makedirs(app_dir, exist_ok=True)
        self.db_path = os.path.join(app_dir, "contra_rst.db")
        
        # Ruta de OneDrive
        one_drive_path = os.path.expanduser("~/OneDrive/ContraRST")
        
        # Inicializar gestor de sincronización
        self.sync_manager = OneDriveSyncManager(self.db_path, one_drive_path)
        
        # Intentar cargar desde OneDrive
        success, msg = self.sync_manager.cargar_db()
        if not success and "No se encontró" in msg:
            # Crear base de datos nueva
            self.db_manager = DatabaseManager(self.db_path)
            self.db_manager.crear_tablas()
            self.db_manager.insertar_datos_iniciales()
            # Sincronizar con OneDrive
            self.sync_manager.sincronizar_db()
        else:
            # Conectar a la base de datos existente
            self.db_manager = DatabaseManager(self.db_path)

        # También aplica tablas nuevas cuando se actualiza una instalación existente.
        self.db_manager.crear_tablas()
        self.business_name = self.db_manager.obtener_parametro(
            'EMPRESA_NOMBRE', APP_NAME
        ) or APP_NAME
    
    def create_sidebar(self):
        """Crea el menú lateral"""
        sidebar = toga.Box(
            style=Pack(
                direction=COLUMN,
                width=240,
                margin=15,
                background_color=COLORS['sidebar_background'],
                flex=False
            )
        )
        
        # Logo
        logo = toga.Box(style=Pack(direction=COLUMN, margin_bottom=20))
        logo.add(
            toga.Label(self.business_name, style=Pack(font_size=22, font_weight="bold", color=COLORS['white'])),
            toga.Label(f"{self.user} · Admin", style=Pack(font_size=12, color=COLORS['gray_300']))
        )
        sidebar.add(logo)
        
        # Divisor
        sidebar.add(toga.Divider(style=Pack(margin_bottom=15)))
        
        # Opciones del menú
        menu_items = [
            ("🏠", "Dashboard", self.show_dashboard),
            ("🛒", "Ventas", self.show_ventas),
            ("📦", "Inventario", self.show_inventario),
            ("📊", "Contabilidad", self.show_libro_diario),
            ("📈", "Reportes", self.show_reportes),
        ]
        
        for icon, text, handler in menu_items:
            btn = toga.Button(
                f"{icon} {text}",
                on_press=handler,
                style=Pack(
                    margin=10,
                    background_color=COLORS['sidebar_background'],
                    color=COLORS['white'],
                    font_size=14,
                    text_align="left",
                    width=210
                )
            )
            sidebar.add(btn)
        
        # Divisor
        sidebar.add(toga.Divider(style=Pack(margin_top=20, margin_bottom=10)))
        
        # Configuración y salir
        sidebar.add(
            toga.Button(
                "⚙️ Configuración",
                on_press=self.show_configuracion,
                style=Pack(margin=10, background_color=COLORS['sidebar_background'], color=COLORS['white'], text_align="left")
            )
        )
        sidebar.add(
            toga.Button(
                "🚪 Salir",
                on_press=self.salir_app,
                style=Pack(margin=10, background_color=COLORS['sidebar_background'], color=COLORS['white'], text_align="left")
            )
        )
        
        return sidebar
    
    def show_view(self, view_class, *args, **kwargs):
        """Muestra una vista en el contenido principal"""
        # Limpiar contenido actual
        self.content_box.clear()
        
        # Crear la nueva vista
        view = view_class(self, self.db_manager, *args, **kwargs)
        self.current_view = view
        self.content_box.add(view.build())
    
    def show_dashboard(self, widget=None):
        self.show_view(DashboardView)
    
    def show_inventario(self, widget=None):
        self.show_view(InventarioView)
    
    def show_ventas(self, widget=None):
        self.show_view(VentasView)
    
    def show_libro_diario(self, widget=None):
        self.show_view(ContabilidadView, 'diario')
    
    def show_libro_mayor(self, widget=None):
        self.show_view(ContabilidadView, 'mayor')
    
    def show_conciliacion(self, widget=None):
        self.show_view(ContabilidadView, 'conciliacion')
    
    def show_rst_iva(self, widget=None):
        self.show_view(ContabilidadView, 'rst_iva')
    
    def show_reportes(self, widget=None):
        self.show_view(ReportesView)
    
    def show_puc(self, widget=None):
        self.show_view(ContabilidadView, 'puc')
    
    def show_configuracion(self, widget=None):
        self.show_view(ConfiguracionView)

    def show_asientos(self, widget=None):
        self.show_view(AsientosView)
    
    def salir_app(self, widget=None):
        """Cierra la aplicación y sincroniza"""
        if self.sync_manager:
            self.sync_manager.sincronizar_db()
        self.main_window.close()

def main():
    return ContraRSTApp(
        APP_NAME,
        "com.whenterprise.inventario_petmarket"
    )

if __name__ == "__main__":
    main().main_loop()