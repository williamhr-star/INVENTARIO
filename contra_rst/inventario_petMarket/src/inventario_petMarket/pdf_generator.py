import os
import sqlite3
from datetime import datetime
from . import APP_NAME

# ⭐ INTENTAR IMPORTAR REPORTLAB (solo funciona en escritorio)
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    # Definimos placeholders para que el código no falle al referenciarlos
    colors = None
    A4 = None
    SimpleDocTemplate = None
    Table = None
    TableStyle = None
    Paragraph = None
    Spacer = None
    getSampleStyleSheet = None
    ParagraphStyle = None
    inch = None


class PDFGenerator:
    """Generador de reportes PDF (solo disponible en escritorio)"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.output_dir = os.path.expanduser("~/OneDrive/ContraRST/reportes")
        os.makedirs(self.output_dir, exist_ok=True)

    def is_available(self) -> bool:
        """Indica si la generación de PDF está disponible en esta plataforma."""
        return REPORTLAB_AVAILABLE

    def _nombre_empresa(self) -> str:
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT valor FROM parametros WHERE clave = 'EMPRESA_NOMBRE'"
            ).fetchone()
            return (row[0] if row and row[0] else None) or APP_NAME
        finally:
            conn.close()
    
    def generar_estado_resultados(self, desde: str, hasta: str) -> str:
        """Genera el estado de resultados en PDF (solo escritorio)."""
        if not REPORTLAB_AVAILABLE:
            return "❌ Generación de PDF no disponible en esta plataforma"
        
        try:
            filename = os.path.join(self.output_dir, f"estado_resultados_{datetime.now().strftime('%Y%m%d')}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Estilo de título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.blue,
                alignment=1
            )
            
            story.append(Paragraph(self._nombre_empresa(), title_style))
            story.append(Paragraph("ESTADO DE RESULTADOS", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"Período: {desde} al {hasta}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Obtener datos
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("SELECT COALESCE(SUM(debito), 0) FROM asientos WHERE cuenta LIKE '4%' AND fecha BETWEEN ? AND ?", (desde, hasta))
            ingresos = c.fetchone()[0]
            
            c.execute("SELECT COALESCE(SUM(debito), 0) FROM asientos WHERE cuenta LIKE '6135%' AND fecha BETWEEN ? AND ?", (desde, hasta))
            costos_venta = c.fetchone()[0]
            
            c.execute("SELECT COALESCE(SUM(debito), 0) FROM asientos WHERE (cuenta LIKE '5%' OR cuenta LIKE '6%') AND fecha BETWEEN ? AND ?", (desde, hasta))
            gastos = c.fetchone()[0]
            
            conn.close()
            
            utilidad_bruta = ingresos - costos_venta
            utilidad_neta = utilidad_bruta - gastos
            
            # Tabla de resultados
            data = [
                ['Concepto', 'Valor'],
                ['Ingresos', f'${ingresos:,.0f}'],
                ['(-) Costo de Ventas', f'${costos_venta:,.0f}'],
                ['Utilidad Bruta', f'${utilidad_bruta:,.0f}'],
                ['(-) Gastos Operativos', f'${gastos:,.0f}'],
                ['Utilidad Neta', f'${utilidad_neta:,.0f}'],
            ]
            
            table = Table(data, colWidths=[4*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 5), (-1, 5), colors.lightgrey),
            ]))
            story.append(table)
            
            doc.build(story)
            return filename
        
        except Exception as e:
            return f"❌ Error al generar PDF: {str(e)}"

    def generar_inventario_valorizado(self) -> str:
        """Genera un PDF con el inventario actual y su valor total (solo escritorio)."""
        if not REPORTLAB_AVAILABLE:
            return "❌ Generación de PDF no disponible en esta plataforma"
        
        try:
            filename = os.path.join(
                self.output_dir,
                f"inventario_valorizado_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'InventoryTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.blue,
                alignment=1
            )
            story = [
                Paragraph(self._nombre_empresa(), title_style),
                Paragraph("INVENTARIO VALORIZADO", styles['Heading2']),
                Spacer(1, 0.2 * inch),
                Paragraph(
                    f"Fecha: {datetime.now().strftime('%Y-%m-%d')}",
                    styles['Normal']
                ),
                Spacer(1, 0.3 * inch),
            ]

            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT codigo, nombre, stock_actual, precio_costo,
                           stock_actual * precio_costo AS valor_total
                    FROM productos
                    ORDER BY nombre
                ''')
                productos = cursor.fetchall()
            finally:
                conn.close()

            data = [['Código', 'Producto', 'Stock', 'Costo unitario', 'Valor total']]
            valor_inventario = 0
            for codigo, nombre, stock, costo, valor_total in productos:
                valor_inventario += valor_total or 0
                data.append([
                    codigo,
                    nombre,
                    f'{stock:,.2f}',
                    f'${costo:,.0f}',
                    f'${valor_total:,.0f}',
                ])
            data.append(['', '', '', 'TOTAL', f'${valor_inventario:,.0f}'])

            table = Table(data, colWidths=[1.0 * inch, 2.5 * inch, 0.8 * inch, 1.1 * inch, 1.1 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ]))
            story.append(table)
            doc.build(story)
            return filename
        
        except Exception as e:
            return f"❌ Error al generar PDF: {str(e)}"

    def _generar_tabla_asientos(self, titulo: str, filename: str, desde: str, hasta: str, query: str, parametros=()):
        """Genera reportes tabulares que parten del libro de asientos (solo escritorio)."""
        if not REPORTLAB_AVAILABLE:
            return "❌ Generación de PDF no disponible en esta plataforma"
        
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                rows = conn.execute(query, (*parametros, desde, hasta)).fetchall()
            finally:
                conn.close()

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = [
                Paragraph(self._nombre_empresa(), ParagraphStyle('ReportTitle', parent=styles['Heading1'], alignment=1, textColor=colors.blue)),
                Paragraph(titulo, styles['Heading2']),
                Spacer(1, 0.2 * inch),
                Paragraph(f"Período: {desde} al {hasta}", styles['Normal']),
                Spacer(1, 0.25 * inch),
            ]
            data = [['Fecha', 'Descripción', 'Cuenta', 'Débito', 'Crédito']]
            data.extend([
                [fecha[:10], descripcion[:32], f'{cuenta} {nombre[:18]}', f'${debito:,.0f}', f'${credito:,.0f}']
                for fecha, descripcion, cuenta, nombre, debito, credito in rows
            ])
            table = Table(data, colWidths=[0.85 * inch, 2.25 * inch, 1.45 * inch, 0.8 * inch, 0.8 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ]))
            story.append(table)
            doc.build(story)
            return filename
        
        except Exception as e:
            return f"❌ Error al generar PDF: {str(e)}"

    def generar_libro_diario(self, desde: str, hasta: str) -> str:
        filename = os.path.join(self.output_dir, f"libro_diario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        return self._generar_tabla_asientos(
            'LIBRO DIARIO', filename, desde, hasta,
            """SELECT fecha, descripcion, cuenta, nombre_cuenta, debito, credito
            FROM asientos WHERE fecha BETWEEN ? AND ? ORDER BY fecha, id"""
        )

    def generar_rst_iva(self, desde: str, hasta: str) -> str:
        filename = os.path.join(self.output_dir, f"rst_iva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        return self._generar_tabla_asientos(
            'RST E IVA', filename, desde, hasta,
            """SELECT fecha, descripcion, cuenta, nombre_cuenta, debito, credito
            FROM asientos WHERE fecha BETWEEN ? AND ? AND (cuenta LIKE '4%' OR cuenta LIKE '24%')
            ORDER BY fecha, id"""
        )