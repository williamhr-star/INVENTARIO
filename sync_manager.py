import os
import shutil
import time
import subprocess
from datetime import datetime
from pathlib import Path

class OneDriveSyncManager:
    """Gestiona la sincronización de la base de datos con OneDrive"""
    
    def __init__(self, db_path: str, one_drive_folder: str):
        self.db_path = db_path
        self.one_drive_folder = one_drive_folder
        
        # Crear directorios si no existen
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(one_drive_folder, exist_ok=True)
        os.makedirs(os.path.join(one_drive_folder, "backups"), exist_ok=True)
        os.makedirs(os.path.join(one_drive_folder, "reportes"), exist_ok=True)
    
    def sincronizar_db(self) -> tuple:
        """Copia la base de datos a OneDrive y fuerza la sincronización"""
        try:
            # 1. Crear backup
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(self.one_drive_folder, "backups", backup_name)
            shutil.copy2(self.db_path, backup_path)
            
            # 2. Copiar la DB a OneDrive
            destino = os.path.join(self.one_drive_folder, "contra_rst.db")
            shutil.copy2(self.db_path, destino)
            
            # 3. Forzar sincronización en Windows
            if os.name == 'nt':
                try:
                    subprocess.run(
                        ["powershell", "-Command", "Start-Process 'onedrive.exe' -ArgumentList '/sync'"],
                        capture_output=True,
                        timeout=5
                    )
                except:
                    pass
            
            return True, f"✅ Sincronizado: {backup_name}"
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def cargar_db(self) -> tuple:
        """Carga la base de datos desde OneDrive a la máquina local"""
        origen = os.path.join(self.one_drive_folder, "contra_rst.db")
        
        if os.path.exists(origen):
            try:
                shutil.copy2(origen, self.db_path)
                return True, "✅ Base de datos cargada desde OneDrive"
            except Exception as e:
                return False, f"❌ Error al cargar: {str(e)}"
        else:
            return False, "ℹ️ No se encontró base de datos en OneDrive, se creará una nueva"
    
    def crear_estructura_inicial(self):
        """Crea la estructura de carpetas en OneDrive"""
        os.makedirs(os.path.join(self.one_drive_folder, "backups"), exist_ok=True)
        os.makedirs(os.path.join(self.one_drive_folder, "reportes"), exist_ok=True)