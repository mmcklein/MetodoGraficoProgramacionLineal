"""
Capa de presentación — Gráfica.
Widget reutilizable que embebe una figura matplotlib dentro de un frame Tkinter.
"""

import tkinter as tk
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Polygon as MplPolygon
from scipy.spatial import ConvexHull

from graphlp_config import COLORS


class PanelGrafico:
    """
    Panel que contiene la gráfica interactiva del método gráfico de PL.
    Se instancia pasándole el frame padre de Tkinter.
    """

    def __init__(self, parent_frame: tk.Frame):
        self.fig = Figure(figsize=(8.5, 6.5), dpi=100, facecolor=COLORS["bg_card"])
        self.ax  = self.fig.add_subplot(111)
        self._estilizar()

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        tb_frame = tk.Frame(parent_frame, bg=COLORS["bg_card"])
        tb_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.toolbar = NavigationToolbar2Tk(self.canvas, tb_frame)
        self.toolbar.config(background=COLORS["bg_card"])
        self.toolbar.update()

        # Guardará la ruta de la última imagen exportada
        self.ultima_ruta_imagen: str = ""

    # ------------------------------------------------------------------
    def _estilizar(self):
        """Aplica el estilo base al eje."""
        self.ax.set_facecolor(COLORS["plot_bg"])
        self.ax.grid(True, linestyle="--", alpha=0.5, color="#C8CDD2", zorder=0)
        for s in ["top", "right"]:
            self.ax.spines[s].set_visible(False)
        for s in ["left", "bottom"]:
            self.ax.spines[s].set_color(COLORS["border"])
        self.ax.tick_params(colors=COLORS["text_muted"], labelsize=8)
        self.ax.set_xlabel("x₁", fontsize=10, color=COLORS["text_dark"], fontweight="bold")
        self.ax.set_ylabel("x₂", fontsize=10, color=COLORS["text_dark"], fontweight="bold")

    # ------------------------------------------------------------------
    def limpiar(self):
        """Limpia la gráfica y muestra el estado inicial."""
        self.ax.cla()
        self._estilizar()
        self.ax.set_title(
            "Región Factible",
            fontsize=11, color=COLORS["text_dark"], fontweight="bold", pad=10,
        )
        self.canvas.draw()
        self.ultima_ruta_imagen = ""

    # ------------------------------------------------------------------
    def graficar(
        self,
        c_obj,
        A_ub, b_ub,
        A_eq, b_eq,
        resultado: dict,
        maximizar: bool,
        ruta_exportar: str = "",
    ) -> str:
        """
        Dibuja la región factible, las restricciones y el punto óptimo.

        Parámetros
        ----------
        c_obj        : [float, float]  coeficientes de la F.O.
        A_ub, b_ub   : coeficientes y lados derechos de restricciones <=
        A_eq, b_eq   : coeficientes y lados derechos de restricciones =
        resultado    : dict devuelto por MotorMatematico.resolver()
        maximizar    : bool
        ruta_exportar: str  ruta donde guardar la imagen PNG (opcional)

        Devuelve la ruta de la imagen guardada (cadena vacía si no se guardó).
        """
        self.ax.cla()
        self._estilizar()

        tipo_str = "Maximización" if maximizar else "Minimización"
        self.ax.set_title(
            f"Método Gráfico — {tipo_str}",
            fontsize=11, color=COLORS["text_dark"], fontweight="bold", pad=12,
        )

        vertices = resultado.get("vertices", [])
        x_opt    = resultado.get("x_opt")

        # Calcular margen
        ref = 10.0
        if x_opt is not None:
            ref = max(float(x_opt[0]), float(x_opt[1]), 1.0)
        elif vertices:
            ref = max(max(float(v[0]) for v in vertices),
                      max(float(v[1]) for v in vertices), 1.0)
        margen = ref * 1.6 + 2
        xx = np.linspace(0, margen, 600)

        colores_l = ["#0D6EFD", "#6F42C1", "#FD7E14", "#20C997", "#E83E8C", "#17A2B8"]
        leyenda   = []
        idx       = 0

        # Restricciones <=
        if A_ub:
            for i, (a, b) in enumerate(zip(A_ub, b_ub)):
                a1, a2 = float(a[0]), float(a[1])
                col = colores_l[idx % len(colores_l)]; idx += 1
                if abs(a2) > 1e-9:
                    yy = (b - a1 * xx) / a2
                    self.ax.plot(xx, yy, color=col, linewidth=1.8,
                                 linestyle="--", alpha=0.85, zorder=2)
                    leyenda.append(mpatches.Patch(
                        color=col,
                        label=f"R{i+1}: {a1:g}x₁+{a2:g}x₂≤{b:g}",
                    ))
                elif abs(a1) > 1e-9:
                    self.ax.axvline(x=b / a1, color=col, linewidth=1.8,
                                    linestyle="--", alpha=0.85, zorder=2)
                    leyenda.append(mpatches.Patch(
                        color=col, label=f"R{i+1}: {a1:g}x₁≤{b:g}",
                    ))

        # Restricciones =
        if A_eq:
            for i, (a, b) in enumerate(zip(A_eq, b_eq)):
                a1, a2 = float(a[0]), float(a[1])
                col = colores_l[idx % len(colores_l)]; idx += 1
                if abs(a2) > 1e-9:
                    yy = (b - a1 * xx) / a2
                    self.ax.plot(xx, yy, color=col, linewidth=2.0, zorder=2)
                    leyenda.append(mpatches.Patch(
                        color=col, label=f"Eq{i+1}: {a1:g}x₁+{a2:g}x₂={b:g}",
                    ))

        # Región factible (polígono convexo)
        if len(vertices) >= 3:
            try:
                pts  = np.array(vertices)
                hull = ConvexHull(pts)
                hull_pts = pts[hull.vertices]
                self.ax.add_patch(MplPolygon(
                    hull_pts, closed=True,
                    facecolor=COLORS["feasible"], alpha=0.18,
                    edgecolor=COLORS["feasible"], linewidth=1.5, zorder=1,
                ))
                leyenda.append(mpatches.Patch(
                    facecolor=COLORS["feasible"], alpha=0.4, label="Región Factible",
                ))
            except Exception:
                pass

        # Vértices
        for v in vertices:
            self.ax.plot(v[0], v[1], "o",
                         color=COLORS["primary"], markersize=6,
                         zorder=4, markeredgecolor="white", markeredgewidth=1.2)
            self.ax.annotate(
                f"({v[0]:.2f},{v[1]:.2f})",
                xy=(v[0], v[1]), xytext=(5, 7), textcoords="offset points",
                fontsize=7.5, color=COLORS["text_dark"], zorder=5,
            )

        # Punto óptimo
        if x_opt is not None:
            z_val = resultado.get("z_opt", 0)
            self.ax.plot(x_opt[0], x_opt[1], "*",
                         color=COLORS["optimal_pt"], markersize=18,
                         zorder=6, markeredgecolor="white", markeredgewidth=1.5)
            self.ax.annotate(
                f"  Z* = {z_val:.4f}\n  ({x_opt[0]:.4f}, {x_opt[1]:.4f})",
                xy=(x_opt[0], x_opt[1]), xytext=(10, -18), textcoords="offset points",
                fontsize=8.5, color=COLORS["optimal_pt"], fontweight="bold", zorder=7,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=COLORS["optimal_pt"], alpha=0.9),
            )
            leyenda.append(mpatches.Patch(
                facecolor=COLORS["optimal_pt"],
                label=f"Óptimo: ({x_opt[0]:.3f}, {x_opt[1]:.3f})",
            ))

        # Ejes y límites
        self.ax.axhline(0, color=COLORS["text_dark"], linewidth=0.8, zorder=3)
        self.ax.axvline(0, color=COLORS["text_dark"], linewidth=0.8, zorder=3)
        self.ax.set_xlim(-0.5, margen)
        self.ax.set_ylim(-0.5, margen)

        if leyenda:
            self.ax.legend(
                handles=leyenda, loc="upper right", fontsize=7.5,
                framealpha=0.92, edgecolor=COLORS["border"], fancybox=True,
            )

        self.fig.tight_layout(pad=1.5)
        self.canvas.draw()

        # Exportar imagen si se indicó ruta
        if ruta_exportar:
            self.fig.savefig(ruta_exportar, dpi=150, bbox_inches="tight")
            self.ultima_ruta_imagen = ruta_exportar

        return self.ultima_ruta_imagen
