import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from inventario_petMarket.database import DatabaseManager


def test_first():
    """An initial test for the app."""
    assert 1 + 1 == 2


def test_parametro_empresa_y_un_debito_a_caja(tmp_path):
    db = DatabaseManager(str(tmp_path / "test.db"))
    db.crear_tablas()
    db.insertar_datos_iniciales()

    assert db.obtener_parametro("EMPRESA_NOMBRE") == "Mi Empresa"

    producto = db.obtener_productos()[0]
    venta_id = db.registrar_venta(
        {
            "cliente": "Cliente de prueba",
            "subtotal": 3500,
            "iva": 665,
            "total": 4165,
        },
        [{
            "producto_id": producto["id"],
            "cantidad": 1,
            "precio_unitario": 3500,
            "subtotal": 3500,
        }],
    )

    conn = db.conectar()
    try:
        cantidad_caja = conn.execute(
            "SELECT COUNT(*) FROM asientos "
            "WHERE cuenta = '1105' AND documento_referencia = ?",
            (str(venta_id),),
        ).fetchone()[0]
    finally:
        conn.close()

    assert cantidad_caja == 1
