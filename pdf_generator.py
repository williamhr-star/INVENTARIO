import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import sqlite3
from datetime import datetime

class PDFGenerator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.output_dir = os.path.expanduser("~/OneDrive/ContraRST/reportes")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generar_estado_resultados(self, desde: str, hasta: str) -> str:
        """Genera el estado de resultados en PDF"""
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
        
        story.append(Paragraph("ESTADO DE RESULTADOS", title_style))
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

    def generar_inventario_valorizado(self) -> str:
        """Genera un PDF con el inventario actual y su valor total."""
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
            Paragraph("INVENTARIO VALORIZADO", title_style),
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