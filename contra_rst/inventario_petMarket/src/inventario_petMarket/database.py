import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        
    def conectar(self):
        """Establece conexión con la base de datos"""
        self.conn = sqlite3.connect(self.db_path, timeout=10)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def cerrar(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()
    
    def crear_tablas(self):
        """Crea todas las tablas necesarias"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                categoria TEXT,
                unidad_medida TEXT,
                stock_actual REAL DEFAULT 0,
                stock_minimo REAL DEFAULT 0,
                stock_maximo REAL DEFAULT 0,
                precio_costo REAL DEFAULT 0,
                precio_venta REAL DEFAULT 0,
                ubicacion TEXT,
                fecha_creacion TEXT,
                ultima_actualizacion TEXT
            )
        ''')
        
        # Tabla de compras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                fecha TEXT,
                factura TEXT,
                proveedor TEXT,
                cantidad REAL,
                valor_unitario REAL,
                valor_total REAL,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # Tabla de movimientos de inventario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                fecha TEXT,
                tipo TEXT,
                cantidad REAL,
                saldo_anterior REAL,
                saldo_nuevo REAL,
                motivo TEXT,
                documento_referencia TEXT,
                usuario TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # Tabla de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                cliente TEXT,
                tipo_comprobante TEXT,
                numero_comprobante TEXT,
                subtotal REAL,
                iva REAL,
                total REAL,
                estado TEXT,
                usuario TEXT
            )
        ''')
        
        # Tabla de detalle de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                producto_id INTEGER,
                cantidad REAL,
                precio_unitario REAL,
                descuento REAL,
                subtotal REAL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')

        # Métodos de pago separados para permitir pagos divididos.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                metodo TEXT NOT NULL,
                monto REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id)
            )
        ''')
        
        # Tabla de asientos contables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                descripcion TEXT,
                cuenta TEXT,
                nombre_cuenta TEXT,
                debito REAL DEFAULT 0,
                credito REAL DEFAULT 0,
                documento_referencia TEXT,
                tipo_movimiento TEXT,
                usuario TEXT
            )
        ''')
        
        # Tabla de parámetros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parametros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT UNIQUE NOT NULL,
                valor TEXT,
                descripcion TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                usuario TEXT NOT NULL,
                accion TEXT NOT NULL,
                entidad TEXT NOT NULL,
                entidad_id INTEGER,
                detalle TEXT
            )
        ''')

        cursor.execute(
            "INSERT OR IGNORE INTO parametros (clave, valor, descripcion) VALUES (?, ?, ?)",
            ('META_DIA', '1000000', 'Meta diaria de ventas')
        )
        
        conn.commit()
        self.cerrar()
    
    def insertar_datos_iniciales(self):
        """Inserta datos iniciales en la base de datos"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Parámetros iniciales
        parametros_iniciales = [
            ('IVA', '19', 'Porcentaje de IVA'),
            ('RST_TARIFA', '2.5', 'Tarifa RST según actividad'),
            ('EMPRESA_NOMBRE', 'Mi Empresa', 'Nombre de la empresa'),
            ('EMPRESA_NIT', '900.000.000-0', 'NIT de la empresa'),
            ('EMPRESA_DIRECCION', 'Calle 123', 'Dirección'),
            ('EMPRESA_TELEFONO', '3000000000', 'Teléfono'),
            ('META_DIA', '1000000', 'Meta diaria de ventas'),
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO parametros (clave, valor, descripcion) VALUES (?, ?, ?)',
            parametros_iniciales
        )
        
        # Productos de ejemplo
        productos_ejemplo = [
            ('PROD-001', 'Harina de Trigo', 'Alimentos', 'kg', 100, 20, 500, 2000, 3500, 'Bodega A'),
            ('PROD-002', 'Azúcar Blanca', 'Alimentos', 'kg', 50, 10, 200, 1800, 3000, 'Bodega A'),
            ('PROD-003', 'Aceite Vegetal', 'Alimentos', 'litro', 30, 5, 100, 4500, 7000, 'Bodega B'),
        ]
        
        cursor.executemany(
            '''INSERT OR IGNORE INTO productos 
            (codigo, nombre, categoria, unidad_medida, stock_actual, stock_minimo, stock_maximo, precio_costo, precio_venta, ubicacion, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            [(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], datetime.now().isoformat()) for p in productos_ejemplo]
        )
        
        conn.commit()
        self.cerrar()

    def obtener_parametro(self, clave: str, predeterminado=None):
        """Obtiene un parámetro de configuración o devuelve un valor alternativo."""
        conn = self.conectar()
        try:
            resultado = conn.execute(
                "SELECT valor FROM parametros WHERE clave = ?", (clave,)
            ).fetchone()
            return resultado[0] if resultado else predeterminado
        finally:
            conn.close()
    
    # ========== MÉTODOS CRUD PARA PRODUCTOS ==========
    def obtener_productos(self, solo_stock_bajo=False) -> List[Dict]:
        """Obtiene todos los productos"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        query = "SELECT * FROM productos"
        if solo_stock_bajo:
            query += " WHERE stock_actual < stock_minimo"
        query += " ORDER BY nombre"
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in resultados]
    
    def obtener_producto(self, producto_id: int) -> Optional[Dict]:
        """Obtiene un producto por ID"""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        resultado = cursor.fetchone()
        conn.close()
        return dict(resultado) if resultado else None
    
    def crear_producto(self, datos: Dict) -> int:
        """Crea un nuevo producto"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO productos 
            (codigo, nombre, categoria, unidad_medida, stock_actual, stock_minimo, 
             stock_maximo, precio_costo, precio_venta, ubicacion, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos['codigo'],
            datos['nombre'],
            datos.get('categoria', ''),
            datos.get('unidad_medida', 'unidad'),
            datos.get('stock_actual', 0),
            datos.get('stock_minimo', 0),
            datos.get('stock_maximo', 1000),
            datos.get('precio_costo', 0),
            datos.get('precio_venta', 0),
            datos.get('ubicacion', ''),
            datetime.now().isoformat()
        ))
        
        producto_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return producto_id
    
    def actualizar_producto(self, producto_id: int, datos: Dict) -> bool:
        """Actualiza un producto existente"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        campos = []
        valores = []
        for key, value in datos.items():
            if key != 'id':
                campos.append(f"{key} = ?")
                valores.append(value)
        
        valores.append(producto_id)
        query = f"UPDATE productos SET {', '.join(campos)}, ultima_actualizacion = ? WHERE id = ?"
        valores.insert(-1, datetime.now().isoformat())
        
        cursor.execute(query, valores)
        conn.commit()
        afectados = cursor.rowcount
        conn.close()
        return afectados > 0
    
    def actualizar_stock(self, producto_id: int, cantidad: float, motivo: str, usuario: str) -> bool:
        """Actualiza el stock de un producto y registra el movimiento"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Obtener stock actual
        cursor.execute("SELECT stock_actual FROM productos WHERE id = ?", (producto_id,))
        resultado = cursor.fetchone()
        if not resultado:
            conn.close()
            return False
        
        stock_anterior = resultado[0]
        stock_nuevo = stock_anterior + cantidad
        
        # Actualizar stock
        cursor.execute(
            "UPDATE productos SET stock_actual = ?, ultima_actualizacion = ? WHERE id = ?",
            (stock_nuevo, datetime.now().isoformat(), producto_id)
        )
        
        # Registrar movimiento
        tipo = 'ENTRADA' if cantidad > 0 else 'SALIDA'
        cursor.execute('''
            INSERT INTO movimientos_inventario 
            (producto_id, fecha, tipo, cantidad, saldo_anterior, saldo_nuevo, motivo, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (producto_id, datetime.now().isoformat(), tipo, cantidad, stock_anterior, stock_nuevo, motivo, usuario))
        
        conn.commit()
        conn.close()
        return True

    def eliminar_producto(self, producto_id: int, usuario: str) -> bool:
        """Elimina un producto sin ventas asociadas y registra la auditoría."""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        if not producto:
            conn.close()
            return False
        cursor.execute("SELECT 1 FROM detalle_ventas WHERE producto_id = ? LIMIT 1", (producto_id,))
        if cursor.fetchone():
            conn.close()
            raise ValueError("No se puede eliminar un producto con ventas asociadas")
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        cursor.execute('''
            INSERT INTO auditoria (fecha, usuario, accion, entidad, entidad_id, detalle)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), usuario, 'ELIMINAR', 'producto', producto_id, producto['nombre']))
        conn.commit()
        conn.close()
        return True
    
    # ========== MÉTODOS CRUD PARA VENTAS ==========
    def registrar_venta(self, datos_venta: Dict, detalles: List[Dict], pagos: Optional[List[Dict]] = None) -> int:
        """Registra una venta completa con sus detalles"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Insertar venta
        cursor.execute('''
            INSERT INTO ventas 
            (fecha, cliente, tipo_comprobante, numero_comprobante, subtotal, iva, total, estado, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            datos_venta.get('cliente', 'Cliente General'),
            datos_venta.get('tipo_comprobante', 'Boleta'),
            datos_venta.get('numero_comprobante', ''),
            datos_venta['subtotal'],
            datos_venta.get('iva', 0),
            datos_venta['total'],
            'Pagada',
            datos_venta.get('usuario', 'Admin')
        ))
        
        venta_id = cursor.lastrowid

        for pago in pagos or []:
            cursor.execute(
                'INSERT INTO pagos_venta (venta_id, metodo, monto) VALUES (?, ?, ?)',
                (venta_id, pago['metodo'], pago['monto'])
            )
        
        # Insertar detalles y actualizar stock
        for detalle in detalles:
            cursor.execute('''
                INSERT INTO detalle_ventas 
                (venta_id, producto_id, cantidad, precio_unitario, descuento, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                venta_id,
                detalle['producto_id'],
                detalle['cantidad'],
                detalle['precio_unitario'],
                detalle.get('descuento', 0),
                detalle['subtotal']
            ))      
            
            # Actualizar stock dentro de la transacción de la venta.
            cursor.execute(
                "SELECT stock_actual, precio_costo FROM productos WHERE id = ?",
                (detalle['producto_id'],)
            )
            producto = cursor.fetchone()
            if not producto:
                raise ValueError(f"Producto no encontrado: {detalle['producto_id']}")

            stock_anterior = producto['stock_actual']
            stock_nuevo = stock_anterior - detalle['cantidad']
            if stock_nuevo < 0:
                raise ValueError(f"Stock insuficiente para el producto {detalle['producto_id']}")

            cursor.execute(
                "UPDATE productos SET stock_actual = ?, ultima_actualizacion = ? WHERE id = ?",
                (stock_nuevo, datetime.now().isoformat(), detalle['producto_id'])
            )
            cursor.execute('''
                INSERT INTO movimientos_inventario
                (producto_id, fecha, tipo, cantidad, saldo_anterior, saldo_nuevo, motivo, usuario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                detalle['producto_id'], datetime.now().isoformat(), 'SALIDA',
                -detalle['cantidad'], stock_anterior, stock_nuevo,
                f"Venta #{venta_id}", datos_venta.get('usuario', 'Admin')
            ))
            
            # Registrar asiento contable de costo de venta
            costo_total = producto['precio_costo'] * detalle['cantidad']
                
            # Débito a Costo de Ventas
            cursor.execute('''
                    INSERT INTO asientos 
                    (fecha, descripcion, cuenta, nombre_cuenta, debito, credito, documento_referencia, tipo_movimiento, usuario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    f"Costo de Venta #{venta_id}",
                    '6135',
                    'Costo de Ventas',
                    costo_total,
                    0,
                    str(venta_id),
                    'COSTO_VENTA',
                    datos_venta.get('usuario', 'Admin')
            ))
                
            # Crédito a Inventario
            cursor.execute('''
                INSERT INTO asientos 
                (fecha, descripcion, cuenta, nombre_cuenta, debito, credito, documento_referencia, tipo_movimiento, usuario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                f"Inventario Venta #{venta_id}",
                '1435',
                'Inventario',
                0,
                costo_total,
                str(venta_id),
                'COSTO_VENTA',
                datos_venta.get('usuario', 'Admin')
            ))
        # Registrar asiento contable de ingreso por venta
        cursor.execute('''
            INSERT INTO asientos 
            (fecha, descripcion, cuenta, nombre_cuenta, debito, credito, documento_referencia, tipo_movimiento, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            f"Venta #{venta_id}",
            '1105',
            'Caja',
            datos_venta['total'],
            0,
            str(venta_id),
            'VENTA',
            datos_venta.get('usuario', 'Admin')
        ))
        
        cursor.execute('''
            INSERT INTO asientos 
            (fecha, descripcion, cuenta, nombre_cuenta, debito, credito, documento_referencia, tipo_movimiento, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            f"Ingreso Venta #{venta_id}",
            '4135',
            'Ingresos',
            0,
            datos_venta['total'],
            str(venta_id),
            'VENTA',
            datos_venta.get('usuario', 'Admin')
        ))
        
        conn.commit()
        conn.close()
        return venta_id
    
    # ========== MÉTODOS PARA CONTABILIDAD ==========
    def obtener_resumen_periodo(self, fecha_desde: str, fecha_hasta: str) -> Dict:
        """Obtiene el resumen contable del período"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Ingresos (cuentas 4xxx)
        cursor.execute(
            "SELECT COALESCE(SUM(credito), 0) FROM asientos WHERE cuenta LIKE '4%' AND date(fecha) BETWEEN ? AND ?",
            (fecha_desde, fecha_hasta)
        )
        ingresos = cursor.fetchone()[0]
        
        # Costos de venta (6135)
        cursor.execute(
            "SELECT COALESCE(SUM(debito), 0) FROM asientos WHERE cuenta LIKE '6135%' AND date(fecha) BETWEEN ? AND ?",
            (fecha_desde, fecha_hasta)
        )
        costos_venta = cursor.fetchone()[0]
        
        # Gastos (5xxx y 6xxx)
        cursor.execute(
            "SELECT COALESCE(SUM(debito), 0) FROM asientos WHERE (cuenta LIKE '5%' OR cuenta LIKE '6%') AND date(fecha) BETWEEN ? AND ?",
            (fecha_desde, fecha_hasta)
        )
        gastos = cursor.fetchone()[0]
        
        # Obtener tarifa RST
        cursor.execute("SELECT valor FROM parametros WHERE clave = 'RST_TARIFA'")
        tarifa_rst = float(cursor.fetchone()[0] or 2.5)
        
        utilidad_bruta = ingresos - costos_venta
        utilidad_neta = utilidad_bruta - gastos
        rst_estimado = ingresos * (tarifa_rst / 100)
        
        conn.close()
        
        return {
            'ingresos': ingresos,
            'gastos': gastos,
            'costos_venta': costos_venta,
            'utilidad_bruta': utilidad_bruta,
            'utilidad_neta': utilidad_neta,
            'rst_estimado': rst_estimado
        }

    def obtener_dashboard(self, fecha: Optional[str] = None) -> Dict:
        """Obtiene indicadores diarios, fondos y tendencia para el dashboard."""
        fecha = fecha or datetime.now().strftime('%Y-%m-%d')
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(v.total), 0) AS ventas,
                   COALESCE(SUM(d.cantidad * p.precio_costo), 0) AS cmv
            FROM ventas v
            LEFT JOIN detalle_ventas d ON d.venta_id = v.id
            LEFT JOIN productos p ON p.id = d.producto_id
            WHERE date(v.fecha) = ? AND v.estado = 'Pagada'
        ''', (fecha,))
        indicadores = dict(cursor.fetchone())

        cursor.execute('''
            SELECT pv.metodo, COALESCE(SUM(pv.monto), 0) AS total
            FROM pagos_venta pv JOIN ventas v ON v.id = pv.venta_id
            WHERE date(v.fecha) = ? AND v.estado = 'Pagada'
            GROUP BY pv.metodo ORDER BY pv.metodo
        ''', (fecha,))
        fondos = {row['metodo']: row['total'] for row in cursor.fetchall()}

        cursor.execute('''
            SELECT date(fecha) AS dia, COALESCE(SUM(total), 0) AS total
            FROM ventas WHERE date(fecha) BETWEEN date(?, '-6 days') AND date(?)
            AND estado = 'Pagada' GROUP BY date(fecha) ORDER BY dia
        ''', (fecha, fecha))
        tendencia = {row['dia']: row['total'] for row in cursor.fetchall()}

        cursor.execute("SELECT valor FROM parametros WHERE clave = 'META_DIA'")
        meta_row = cursor.fetchone()
        conn.close()

        ventas = indicadores['ventas'] or 0
        cmv = indicadores['cmv'] or 0
        meta = float(meta_row['valor']) if meta_row and meta_row['valor'] else 0
        return {
            'ventas': ventas,
            'cmv': cmv,
            'margen_bruto': ventas - cmv,
            'meta': meta,
            'cumplimiento': (ventas / meta * 100) if meta else 0,
            'fondos': fondos,
            'tendencia': tendencia,
        }
    
    def obtener_ultimos_asientos(self, limite: int = 10) -> List[Dict]:
        """Obtiene los últimos asientos registrados"""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM asientos ORDER BY fecha DESC, id DESC LIMIT ?",
            (limite,)
        )
        resultados = cursor.fetchall()
        conn.close()
        return [dict(row) for row in resultados]
    
    def obtener_cuentas_clave(self) -> Dict:
        """Obtiene el saldo de cuentas clave"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        cuentas = ['1105', '1305', '1435', '2105', '3115', '4135', '6135']
        resultado = {}
        
        for cuenta in cuentas:
            # Total débitos - total créditos
            cursor.execute(
                "SELECT COALESCE(SUM(debito), 0) - COALESCE(SUM(credito), 0) FROM asientos WHERE cuenta LIKE ?",
                (f"{cuenta}%",)
            )
            saldo = cursor.fetchone()[0]
            
            # Obtener nombre de la cuenta
            cursor.execute(
                "SELECT nombre_cuenta FROM asientos WHERE cuenta LIKE ? LIMIT 1",
                (f"{cuenta}%",)
            )
            nombre = cursor.fetchone()
            nombre_cuenta = nombre[0] if nombre else cuenta
            
            resultado[cuenta] = {
                'saldo': saldo,
                'nombre': nombre_cuenta
            }
        
        conn.close()
        return resultado
    
    def crear_asiento(self, datos: Dict) -> int:
        """Crea un nuevo asiento contable"""
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO asientos 
            (fecha, descripcion, cuenta, nombre_cuenta, debito, credito, documento_referencia, tipo_movimiento, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datos['fecha'],
            datos['descripcion'],
            datos['cuenta'],
            datos.get('nombre_cuenta', ''),
            datos['debito'],
            datos['credito'],
            datos.get('documento_referencia', ''),
            datos.get('tipo_movimiento', 'MANUAL'),
            datos.get('usuario', 'Admin')
        ))
        
        asiento_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return asiento_id