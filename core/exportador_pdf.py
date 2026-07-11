"""
Capa de exportación.
Genera un reporte PDF profesional con el resumen del problema,
la tabla de vértices evaluados y la gráfica del método gráfico.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
)


# Paleta de colores para el reporte
_AZUL_OSCURO  = colors.HexColor("#2E3B55")
_AZUL_CLARO   = colors.HexColor("#E8EDF5")
_VERDE        = colors.HexColor("#198754")
_ROJO         = colors.HexColor("#DC3545")
_GRIS_CLARO   = colors.HexColor("#F8F9FA")
_NEGRO        = colors.black


class ExportadorPDF:
    """
    Genera un reporte PDF a partir de los datos de un problema de PL resuelto.

    Uso:
        exp = ExportadorPDF(directorio_salida="reportes")
        ruta = exp.generar(datos)

    donde `datos` es un dict con las claves documentadas en `generar()`.
    """

    def __init__(self, directorio_salida: str = "reportes"):
        self.directorio_salida = directorio_salida
        os.makedirs(directorio_salida, exist_ok=True)

    # ------------------------------------------------------------------
    def generar(self, datos: dict) -> str:
        """
        Genera el PDF y devuelve la ruta del archivo creado.

        Parámetros esperados en `datos`:
            tipo_problema   : "max" | "min"
            z_coef_a        : float  – coeficiente de X en la F.O.
            z_coef_b        : float  – coeficiente de Y en la F.O.
            restricciones   : list[dict]  – cada dict tiene 'a','b','signo','c','no_neg'
            intersecciones  : list[tuple]  – puntos (x, y) de intersección
            vertices        : list[tuple]  – vértices factibles (x, y)
            optimo          : tuple | None – punto óptimo (x, y)
            valor_optimo    : float | None
            tipo_solucion   : "unica" | "multiple" | "infactible" | "ilimitado"
            ruta_grafica    : str – ruta de la imagen PNG de la gráfica
        """
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_pdf  = os.path.join(self.directorio_salida, f"reporte_{timestamp}.pdf")

        doc   = SimpleDocTemplate(nombre_pdf, pagesize=letter,
                                  leftMargin=0.9*inch, rightMargin=0.9*inch,
                                  topMargin=0.8*inch, bottomMargin=0.8*inch)
        story = self._construir_story(datos)
        doc.build(story)
        return nombre_pdf

    # ------------------------------------------------------------------
    # Construcción del contenido
    # ------------------------------------------------------------------

    def _construir_story(self, d: dict) -> list:
        estilos = self._estilos()
        s       = []

        # ── Encabezado ──────────────────────────────────────────────
        s.append(Paragraph("GraphLP", estilos["titulo"]))
        s.append(Paragraph(
            "Reporte de Solución — Programación Lineal (Método Gráfico)",
            estilos["subtitulo"],
        ))
        s.append(HRFlowable(width="100%", thickness=2, color=_AZUL_OSCURO, spaceAfter=10))
        s.append(Paragraph(
            f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y  %H:%M:%S')}   "
            f"<b>Tipo:</b> {'Maximización' if d['tipo_problema'] == 'max' else 'Minimización'}",
            estilos["normal"],
        ))
        s.append(Spacer(1, 16))

        # ── Función objetivo ─────────────────────────────────────────
        s.append(Paragraph("1. Función Objetivo", estilos["seccion"]))
        fo = (f"Z = {self._fmt(d['z_coef_a'])}·X  +  {self._fmt(d['z_coef_b'])}·Y")
        s.append(Paragraph(fo, estilos["formula"]))
        s.append(Spacer(1, 12))

        # ── Restricciones ────────────────────────────────────────────
        s.append(Paragraph("2. Restricciones del Modelo", estilos["seccion"]))
        rest_items = [
            f"{self._fmt(r['a'])}X + {self._fmt(r['b'])}Y  {r['signo']}  {self._fmt(r['c'])}"
            for r in d["restricciones"]
            if not r.get("no_neg", False)
        ]
        rest_items.append("X ≥ 0 ,  Y ≥ 0  (no negatividad)")
        for idx, texto in enumerate(rest_items, 1):
            s.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{idx}.  {texto}", estilos["normal"]))
        s.append(Spacer(1, 12))

        # ── Intersecciones ───────────────────────────────────────────
        s.append(Paragraph("3. Intersecciones Encontradas", estilos["seccion"]))
        if d["intersecciones"]:
            datos_inter = [["#", "X", "Y"]]
            for i, p in enumerate(d["intersecciones"], 1):
                datos_inter.append([str(i), f"{p[0]:.4f}", f"{p[1]:.4f}"])
            s.append(self._tabla(datos_inter, col_widths=[40, 110, 110]))
        else:
            s.append(Paragraph("No se encontraron intersecciones.", estilos["normal"]))
        s.append(Spacer(1, 12))

        # ── Evaluación en vértices ───────────────────────────────────
        s.append(Paragraph("4. Evaluación de la Función Objetivo en Vértices", estilos["seccion"]))
        if d["vertices"]:
            datos_v = [["Vértice", "X", "Y",
                        f"Z = {self._fmt(d['z_coef_a'])}X + {self._fmt(d['z_coef_b'])}Y"]]
            for i, v in enumerate(d["vertices"], 1):
                z = d["z_coef_a"] * v[0] + d["z_coef_b"] * v[1]
                datos_v.append([f"V{i}", f"{v[0]:.4f}", f"{v[1]:.4f}", f"{z:.4f}"])
            tabla_v = self._tabla(datos_v, col_widths=[55, 90, 90, 175])

            # Resaltar la fila del óptimo si existe
            if d.get("optimo") is not None:
                ox, oy = d["optimo"]
                for fila_idx, v in enumerate(d["vertices"], 1):
                    if abs(v[0] - ox) < 1e-8 and abs(v[1] - oy) < 1e-8:
                        tabla_v.setStyle(TableStyle([
                            ("BACKGROUND", (0, fila_idx), (-1, fila_idx), _AZUL_CLARO),
                            ("FONTNAME",   (0, fila_idx), (-1, fila_idx), "Helvetica-Bold"),
                        ]))
            s.append(tabla_v)
        else:
            s.append(Paragraph("No se encontraron vértices factibles.", estilos["normal"]))
        s.append(Spacer(1, 12))

        # ── Solución óptima ──────────────────────────────────────────
        s.append(Paragraph("5. Solución Óptima", estilos["seccion"]))
        s.append(self._bloque_solucion(d, estilos))
        s.append(Spacer(1, 20))

        # ── Gráfica ──────────────────────────────────────────────────
        ruta_img = d.get("ruta_grafica", "")
        if ruta_img and os.path.exists(ruta_img):
            s.append(Paragraph("6. Representación Gráfica", estilos["seccion"]))
            s.append(Spacer(1, 8))
            s.append(Image(ruta_img, width=6.0 * inch, height=5.0 * inch))

        # ── Pie de página ────────────────────────────────────────────
        s.append(Spacer(1, 20))
        s.append(HRFlowable(width="100%", thickness=1, color=_AZUL_OSCURO))
        s.append(Paragraph(
            "Generado por <b>GraphLP</b> — Sistema de Resolución Gráfica de PL",
            estilos["pie"],
        ))

        return s

    # ------------------------------------------------------------------
    # Bloque de solución
    # ------------------------------------------------------------------

    def _bloque_solucion(self, d: dict, estilos: dict):
        ts = d.get("tipo_solucion", "infactible")

        if ts == "infactible":
            texto = "❌  El problema es <b>INFACTIBLE</b>: no existe región factible que satisfaga todas las restricciones."
            color = _ROJO
        elif ts == "ilimitado":
            texto = "⚠️  La solución es <b>ILIMITADA</b>: la función objetivo crece/decrece indefinidamente."
            color = colors.HexColor("#FD7E14")
        elif ts == "multiple":
            texto = (
                f"🔄  <b>Soluciones múltiples</b>: valor óptimo Z = {d['valor_optimo']:.4f}. "
                "Todos los puntos del segmento entre los vértices con ese valor son óptimos."
            )
            color = _VERDE
        else:
            tipo_txt = "Máximo" if d["tipo_problema"] == "max" else "Mínimo"
            ox, oy   = d["optimo"]
            texto = (
                f"✔  <b>Solución única encontrada</b><br/>"
                f"&nbsp;&nbsp;&nbsp;{tipo_txt} global en:  ({ox:.4f},  {oy:.4f})<br/>"
                f"&nbsp;&nbsp;&nbsp;Valor óptimo de Z:  <b>{d['valor_optimo']:.4f}</b>"
            )
            color = _VERDE

        estilo = ParagraphStyle(
            "solucion",
            parent=estilos["normal"],
            textColor=color,
            fontSize=11,
            leading=16,
        )
        return Paragraph(texto, estilo)

    # ------------------------------------------------------------------
    # Estilos
    # ------------------------------------------------------------------

    def _estilos(self) -> dict:
        base = getSampleStyleSheet()
        return {
            "titulo": ParagraphStyle(
                "titulo",
                parent=base["Heading1"],
                fontSize=26,
                textColor=_AZUL_OSCURO,
                alignment=1,
                spaceAfter=4,
            ),
            "subtitulo": ParagraphStyle(
                "subtitulo",
                parent=base["Heading2"],
                fontSize=12,
                textColor=_AZUL_OSCURO,
                alignment=1,
                spaceAfter=8,
            ),
            "seccion": ParagraphStyle(
                "seccion",
                parent=base["Heading2"],
                fontSize=13,
                textColor=_AZUL_OSCURO,
                spaceBefore=10,
                spaceAfter=6,
                borderPad=3,
            ),
            "normal": ParagraphStyle(
                "normal",
                parent=base["Normal"],
                fontSize=10,
                leading=15,
                spaceAfter=4,
            ),
            "formula": ParagraphStyle(
                "formula",
                parent=base["Normal"],
                fontSize=12,
                leading=18,
                leftIndent=20,
                textColor=_AZUL_OSCURO,
                fontName="Helvetica-Bold",
            ),
            "pie": ParagraphStyle(
                "pie",
                parent=base["Normal"],
                fontSize=8,
                textColor=colors.gray,
                alignment=1,
                spaceBefore=4,
            ),
        }

    # ------------------------------------------------------------------
    # Tabla genérica
    # ------------------------------------------------------------------

    def _tabla(self, datos: list, col_widths: list = None) -> Table:
        t = Table(datos, colWidths=col_widths)
        t.setStyle(TableStyle([
            # Encabezado
            ("BACKGROUND",  (0, 0), (-1, 0), _AZUL_OSCURO),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING",  (0, 0), (-1, 0), 8),
            # Cuerpo
            ("FONTSIZE",    (0, 1), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _GRIS_CLARO]),
            ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
            ("TOPPADDING",  (0, 1), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ]))
        return t

    # ------------------------------------------------------------------

    @staticmethod
    def _fmt(num: float) -> str:
        """Formatea números: enteros sin decimal, flotantes con 2 cifras."""
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}"
