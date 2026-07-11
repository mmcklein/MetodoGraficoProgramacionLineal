"""
Capa de presentación — Interfaz principal (UI mejorada).
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional

from graphlp_config import COLORS, FONTS
from core import MotorMatematico, ExportadorPDF
from ui.panel_grafico import PanelGrafico

# ── Colores propios para botones tk (no ttk) ──────────────────────────
_BTN = {
    "resolver": {"bg": "#198754", "fg": "white", "hover": "#146C43"},
    "limpiar":  {"bg": "#DC3545", "fg": "white", "hover": "#B02A37"},
    "pdf":      {"bg": "#0D6EFD", "fg": "white", "hover": "#0A58CA"},
    "ejemplo":  {"bg": "#FD7E14", "fg": "white", "hover": "#D96308"},
    "agregar":  {"bg": "#0D6EFD", "fg": "white", "hover": "#0A58CA"},
    "eliminar": {"bg": "#6C757D", "fg": "white", "hover": "#565E64"},
}
_BTN_FONT  = ("Segoe UI", 10, "bold")
_BTN_PAD   = {"padx": 14, "pady": 7}

# ── Ejemplos precargados ──────────────────────────────────────────────
EJEMPLOS = {
    "Maximizar ganancias": {
        "tipo": "max", "z": (5, 4),
        "rest": [([6, 4], 24, "<="), ([1, 2], 6, "<=")],
    },
    "Minimizar costos": {
        "tipo": "min", "z": (2, 3),
        "rest": [([1, 1], 4, ">="), ([2, 1], 6, ">=")],
    },
    "Producción mixta": {
        "tipo": "max", "z": (3, 5),
        "rest": [([1, 0], 4, "<="), ([0, 2], 12, "<="), ([3, 2], 18, "<=")],
    },
}


def _btn(parent, text, command, key, width=None):
    """Crea un tk.Button con color, hover y estilo consistente."""
    cfg = _BTN[key]
    kw  = dict(text=text, command=command, font=_BTN_FONT,
               bg=cfg["bg"], fg=cfg["fg"], relief=tk.FLAT,
               cursor="hand2", activebackground=cfg["hover"],
               activeforeground="white", bd=0, **_BTN_PAD)
    if width:
        kw["width"] = width
    b = tk.Button(parent, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=cfg["hover"]))
    b.bind("<Leave>", lambda e: b.config(bg=cfg["bg"]))
    return b


def _tooltip(widget, text):
    """Agrega un tooltip simple a cualquier widget."""
    tip = None

    def show(e):
        nonlocal tip
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 4
        tip = tk.Toplevel(widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        tk.Label(tip, text=text, bg="#FFFFE0", fg="#212529",
                 font=("Segoe UI", 9), relief=tk.SOLID, bd=1,
                 padx=6, pady=3).pack()

    def hide(e):
        nonlocal tip
        if tip:
            tip.destroy()
            tip = None

    widget.bind("<Enter>", show)
    widget.bind("<Leave>", hide)


class AppGraphLP:
    def __init__(self):
        self._restricciones: list = []
        self.resultado: Optional[dict] = None
        self.ruta_grafica: str = ""

        self.motor      = MotorMatematico()
        self.exportador = ExportadorPDF(directorio_salida="reportes")

        os.makedirs("reportes", exist_ok=True)
        os.makedirs("graficas",  exist_ok=True)

        self.root = tk.Tk()
        self.root.title("GraphLP — Método Gráfico de PL")
        self.root.geometry("1350x780")
        self.root.minsize(1000, 650)
        self.root.configure(bg=COLORS["bg_main"])

        self._aplicar_estilo()
        self._construir_ui()
        self.root.mainloop()

    # ── Matrices para el motor ────────────────────────────────────────
    def _matrices(self):
        A_ub, b_ub, A_eq, b_eq = [], [], [], []
        for r in self._restricciones:
            a, b, tipo = r["a"], r["b"], r["tipo"]
            if tipo == "<=":
                A_ub.append(a); b_ub.append(b)
            elif tipo == ">=":
                A_ub.append([-a[0], -a[1]]); b_ub.append(-b)
            else:
                A_eq.append(a); b_eq.append(b)
        return (A_ub or None, b_ub or None, A_eq or None, b_eq or None)

    # ── Estilo ttk ────────────────────────────────────────────────────
    def _aplicar_estilo(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TFrame",            background=COLORS["bg_main"])
        st.configure("TLabel",            background=COLORS["bg_main"],
                     font=FONTS["body"],  foreground=COLORS["text_dark"])
        st.configure("TRadiobutton",      background=COLORS["bg_main"],
                     font=("Segoe UI", 11), foreground=COLORS["text_dark"])
        st.configure("TLabelframe",       background=COLORS["bg_main"])
        st.configure("TLabelframe.Label", background=COLORS["bg_main"],
                     font=("Segoe UI", 11, "bold"), foreground=COLORS["primary"])
        st.configure("TCombobox",         font=("Segoe UI", 11))

    # ── UI principal ──────────────────────────────────────────────────
    def _construir_ui(self):
        # Encabezado
        hdr = tk.Frame(self.root, bg=COLORS["header_bg"], height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  \u2618  GraphLP",
                 bg=COLORS["header_bg"], fg="white",
                 font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT, pady=10)
        tk.Label(hdr, text="Método Gráfico de Programación Lineal",
                 bg=COLORS["header_bg"], fg="#D0E4FF",
                 font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(8, 0), pady=10)

        # Barra de acciones principal (debajo del header)
        self._barra_acciones()

        # Cuerpo
        body = tk.Frame(self.root, bg=COLORS["bg_main"])
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6, 10))

        left = ttk.LabelFrame(body, text="  \U0001f4cb  Datos del Problema", padding=12, width=420)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)

        right = ttk.LabelFrame(body, text="  \U0001f4c8  Gráfica de la Región Factible", padding=6)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._panel_izquierdo(left)
        self.panel_grafico = PanelGrafico(right)

    def _barra_acciones(self):
        bar = tk.Frame(self.root, bg="#E9ECEF", height=52, bd=0)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        b_res = _btn(bar, "  \u25b6  Resolver", self._resolver, "resolver", width=14)
        b_res.pack(side=tk.LEFT, padx=(10, 4), pady=8)
        _tooltip(b_res, "Calcular la solución óptima del problema")

        b_ej = _btn(bar, "  \U0001f4a1  Cargar ejemplo", self._menu_ejemplos, "ejemplo", width=16)
        b_ej.pack(side=tk.LEFT, padx=4, pady=8)
        _tooltip(b_ej, "Cargar un problema de ejemplo predefinido")

        b_lim = _btn(bar, "  \U0001f5d1  Limpiar", self._limpiar, "limpiar", width=12)
        b_lim.pack(side=tk.LEFT, padx=4, pady=8)
        _tooltip(b_lim, "Borrar todos los datos e iniciar desde cero")

        self.btn_pdf = _btn(bar, "  \U0001f4c4  Exportar PDF", self._exportar_pdf, "pdf", width=16)
        self.btn_pdf.config(state=tk.DISABLED, bg="#ADB5BD", activebackground="#ADB5BD")
        self.btn_pdf.pack(side=tk.LEFT, padx=4, pady=8)
        _tooltip(self.btn_pdf, "Generar reporte PDF con gráfica y resultados")

        # Indicador de estado
        self.lbl_estado = tk.Label(bar, text="  Listo para resolver",
                                   bg="#E9ECEF", fg=COLORS["text_muted"],
                                   font=("Segoe UI", 10, "italic"))
        self.lbl_estado.pack(side=tk.RIGHT, padx=14)

    # ── Panel izquierdo ───────────────────────────────────────────────
    def _panel_izquierdo(self, parent):
        # Tipo de problema
        f_tipo = ttk.LabelFrame(parent, text="  \U0001f3af  Tipo de optimización", padding=8)
        f_tipo.pack(fill=tk.X, pady=(0, 8))
        self.tipo_var = tk.StringVar(value="max")
        rb_frame = ttk.Frame(f_tipo)
        rb_frame.pack(anchor=tk.W)
        ttk.Radiobutton(rb_frame, text="\u2b06  Maximizar",
                        variable=self.tipo_var, value="max").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(rb_frame, text="\u2b07  Minimizar",
                        variable=self.tipo_var, value="min").pack(side=tk.LEFT)

        # Función objetivo
        f_fo = ttk.LabelFrame(parent, text="  \U0001f3af  Función Objetivo  Z = c\u2081X\u2081 + c\u2082X\u2082", padding=8)
        f_fo.pack(fill=tk.X, pady=(0, 8))
        fila = ttk.Frame(f_fo)
        fila.pack(anchor=tk.W)
        tk.Label(fila, text="Z =", bg=COLORS["bg_main"],
                 font=("Segoe UI", 12, "bold"), fg=COLORS["primary"]).pack(side=tk.LEFT)
        self.ent_z1 = self._entry(fila, ph="c\u2081", w=8)
        self.ent_z1.pack(side=tk.LEFT, padx=(6, 2))
        tk.Label(fila, text="\u00b7 X\u2081  +", bg=COLORS["bg_main"],
                 font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.ent_z2 = self._entry(fila, ph="c\u2082", w=8)
        self.ent_z2.pack(side=tk.LEFT, padx=(6, 2))
        tk.Label(fila, text="\u00b7 X\u2082", bg=COLORS["bg_main"],
                 font=("Segoe UI", 11)).pack(side=tk.LEFT)
        _tooltip(self.ent_z1, "Coeficiente de X\u2081 en la función objetivo")
        _tooltip(self.ent_z2, "Coeficiente de X\u2082 en la función objetivo")

        # Restricciones
        self._panel_restricciones(parent)

        # Panel de resultado destacado
        self._panel_resultado(parent)

    def _entry(self, parent, ph="", w=7):
        """Entry con estilo."""
        e = tk.Entry(parent, width=w, font=("Segoe UI", 11),
                     bg="white", fg=COLORS["text_dark"],
                     relief=tk.SOLID, bd=1,
                     insertbackground=COLORS["primary"])
        return e

    def _panel_restricciones(self, parent):
        f_rest = ttk.LabelFrame(parent,
                                text="  \U0001f4cb  Restricciones  (a\u2081X\u2081 + a\u2082X\u2082 \u22dc b)",
                                padding=8)
        f_rest.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Lista
        lf = tk.Frame(f_rest, bg=COLORS["bg_main"])
        lf.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        self.lista_rest = tk.Listbox(
            lf, height=5, font=("Consolas", 11),
            bg=COLORS["console_bg"], fg=COLORS["console_text"],
            selectbackground=COLORS["primary"], selectforeground="white",
            activestyle="none", relief=tk.FLAT, bd=0,
        )
        sb = tk.Scrollbar(lf, command=self.lista_rest.yview,
                          bg=COLORS["bg_main"], troughcolor=COLORS["border"])
        self.lista_rest.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_rest.pack(fill=tk.BOTH, expand=True)

        # Fila de entrada
        f_inp = tk.Frame(f_rest, bg=COLORS["bg_main"])
        f_inp.pack(fill=tk.X, pady=(2, 4))
        tk.Label(f_inp, text="a\u2081:", bg=COLORS["bg_main"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_dark"]).pack(side=tk.LEFT)
        self.ent_a1 = self._entry(f_inp, w=5)
        self.ent_a1.pack(side=tk.LEFT, padx=(2, 6))
        tk.Label(f_inp, text="a\u2082:", bg=COLORS["bg_main"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_dark"]).pack(side=tk.LEFT)
        self.ent_a2 = self._entry(f_inp, w=5)
        self.ent_a2.pack(side=tk.LEFT, padx=(2, 6))
        self.signo_var = tk.StringVar(value="<=")
        cb = ttk.Combobox(f_inp, textvariable=self.signo_var,
                          values=["\u2264  (<=)", "\u2265  (>=)", "=  (=)"],
                          width=7, state="readonly", font=("Segoe UI", 10))
        cb.pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(f_inp, text="b:", bg=COLORS["bg_main"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_dark"]).pack(side=tk.LEFT)
        self.ent_b = self._entry(f_inp, w=6)
        self.ent_b.pack(side=tk.LEFT, padx=(2, 8))
        _tooltip(self.ent_a1, "Coeficiente de X\u2081")
        _tooltip(self.ent_a2, "Coeficiente de X\u2082")
        _tooltip(self.ent_b,  "Lado derecho de la restricción")

        # Botones agregar / eliminar
        f_btns2 = tk.Frame(f_rest, bg=COLORS["bg_main"])
        f_btns2.pack(fill=tk.X)
        b_agr = _btn(f_btns2, "  + Agregar", self._agregar_restriccion, "agregar")
        b_agr.pack(side=tk.LEFT, padx=(0, 6))
        b_eli = _btn(f_btns2, "  \u2212 Eliminar", self._eliminar_restriccion, "eliminar")
        b_eli.pack(side=tk.LEFT)
        # Bind Enter en campos para agregar rápido
        for w in (self.ent_a1, self.ent_a2, self.ent_b):
            w.bind("<Return>", lambda e: self._agregar_restriccion())

    def _panel_resultado(self, parent):
        """Panel de resultado con tarjeta destacada + consola de detalle."""
        f_res = ttk.LabelFrame(parent, text="  \U0001f4ca  Resultados", padding=8)
        f_res.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        # Tarjeta de resultado óptimo
        self.card = tk.Frame(f_res, bg=COLORS["border_light"],
                             relief=tk.FLAT, bd=0)
        self.card.pack(fill=tk.X, pady=(0, 6))
        self.lbl_card_titulo = tk.Label(
            self.card, text="Sin resolver",
            bg=COLORS["border_light"], fg=COLORS["text_muted"],
            font=("Segoe UI", 11, "bold"), anchor=tk.W, padx=10, pady=4,
        )
        self.lbl_card_titulo.pack(fill=tk.X)
        self.lbl_card_valor = tk.Label(
            self.card, text="—",
            bg=COLORS["border_light"], fg=COLORS["text_muted"],
            font=("Segoe UI", 16, "bold"), anchor=tk.W, padx=10, pady=2,
        )
        self.lbl_card_valor.pack(fill=tk.X)
        self.lbl_card_punto = tk.Label(
            self.card, text="",
            bg=COLORS["border_light"], fg=COLORS["text_muted"],
            font=("Segoe UI", 10), anchor=tk.W, padx=10,
        )
        self.lbl_card_punto.pack(fill=tk.X, pady=(0, 6))

        # Consola de detalle
        self.txt_resultados = tk.Text(
            f_res, wrap=tk.WORD, height=7,
            font=("Consolas", 9), bg=COLORS["console_bg"],
            fg=COLORS["console_text"], insertbackground="white",
            state=tk.DISABLED, relief=tk.FLAT, bd=0,
        )
        sc = tk.Scrollbar(f_res, command=self.txt_resultados.yview,
                          bg=COLORS["bg_main"], troughcolor=COLORS["border"])
        self.txt_resultados.configure(yscrollcommand=sc.set)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_resultados.pack(fill=tk.BOTH, expand=True)

        # Tags de color para el texto
        self.txt_resultados.tag_configure("ok",    foreground=COLORS["console_text"])
        self.txt_resultados.tag_configure("optimo", foreground=COLORS["console_warn"],
                                          font=("Consolas", 9, "bold"))
        self.txt_resultados.tag_configure("error",  foreground=COLORS["console_err"])
        self.txt_resultados.tag_configure("sep",    foreground=COLORS["text_muted"])
        self.txt_resultados.tag_configure("info",   foreground=COLORS["console_info"])

    # ── Gestión restricciones ─────────────────────────────────────────
    def _signo_real(self):
        """Extrae el signo real del combobox (ignora el texto extra)."""
        v = self.signo_var.get()
        if "<=" in v:  return "<="
        if ">=" in v:  return ">="
        return "="

    def _agregar_restriccion(self):
        try:
            a1 = float(self.ent_a1.get())
            a2 = float(self.ent_a2.get())
            b  = float(self.ent_b.get())
        except ValueError:
            messagebox.showerror("Error de entrada",
                                 "Los coeficientes deben ser números.\n"
                                 "Ejemplo: a\u2081=2  a\u2082=3  b=12")
            return
        signo = self._signo_real()
        self._restricciones.append({"a": [a1, a2], "b": b, "tipo": signo})
        txt = f"  {self._fmt(a1)}X\u2081 + {self._fmt(a2)}X\u2082  {signo}  {self._fmt(b)}"
        self.lista_rest.insert(tk.END, txt)
        for w in (self.ent_a1, self.ent_a2, self.ent_b):
            w.delete(0, tk.END)
        self._set_estado(f"Restricción agregada ({len(self._restricciones)} total)")

    def _eliminar_restriccion(self):
        sel = self.lista_rest.curselection()
        if not sel:
            messagebox.showinfo("Seleccionar",
                                "Haz clic en una restricción de la lista para seleccionarla.")
            return
        self.lista_rest.delete(sel[0])
        self._restricciones.pop(sel[0])
        self._set_estado(f"{len(self._restricciones)} restricciones")

    # ── Ejemplos ─────────────────────────────────────────────────────
    def _menu_ejemplos(self):
        menu = tk.Menu(self.root, tearoff=0, font=("Segoe UI", 10))
        for nombre in EJEMPLOS:
            menu.add_command(label=nombre,
                             command=lambda n=nombre: self._cargar_ejemplo(n))
        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _cargar_ejemplo(self, nombre):
        self._limpiar()
        ej = EJEMPLOS[nombre]
        self.tipo_var.set(ej["tipo"])
        self.ent_z1.insert(0, str(ej["z"][0]))
        self.ent_z2.insert(0, str(ej["z"][1]))
        for coefs, b, signo in ej["rest"]:
            self._restricciones.append({"a": list(coefs), "b": b, "tipo": signo})
            txt = f"  {self._fmt(coefs[0])}X\u2081 + {self._fmt(coefs[1])}X\u2082  {signo}  {self._fmt(b)}"
            self.lista_rest.insert(tk.END, txt)
        self._set_estado(f'Ejemplo cargado: "{nombre}"')

    # ── Resolver ─────────────────────────────────────────────────────
    def _resolver(self):
        try:
            c1 = float(self.ent_z1.get())
            c2 = float(self.ent_z2.get())
        except ValueError:
            messagebox.showerror("Error",
                                 "Ingresa los coeficientes de la función objetivo.\n"
                                 "Ejemplo: c\u2081=5  c\u2082=4")
            return
        if not self._restricciones:
            messagebox.showwarning("Sin restricciones",
                                   "Agrega al menos una restricción antes de resolver.")
            return

        self._set_estado("Calculando...")
        self.root.update_idletasks()

        maximizar = (self.tipo_var.get() == "max")
        c_obj = [c1, c2]
        A_ub, b_ub, A_eq, b_eq = self._matrices()

        self.resultado = self.motor.resolver(c_obj, A_ub, b_ub, A_eq, b_eq, maximizar)
        self._actualizar_card(c_obj, maximizar)
        self._mostrar_detalle(c_obj, maximizar)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.ruta_grafica = os.path.join("graficas", f"grafica_{timestamp}.png")
        self.panel_grafico.graficar(
            c_obj, A_ub, b_ub, A_eq, b_eq,
            self.resultado, maximizar,
            ruta_exportar=self.ruta_grafica,
        )

        if self.resultado["exito"]:
            self._set_estado(f"\u2714 Solución óptima encontrada  |  Z* = {self.resultado['z_opt']:.4f}")
            self._habilitar_pdf(True)
        else:
            self._set_estado("\u26a0  " + self.resultado.get("mensaje", "Sin solución"))
            self._habilitar_pdf(False)

    def _habilitar_pdf(self, ok):
        if ok:
            self.btn_pdf.config(state=tk.NORMAL,
                                bg=_BTN["pdf"]["bg"],
                                activebackground=_BTN["pdf"]["hover"])
        else:
            self.btn_pdf.config(state=tk.DISABLED, bg="#ADB5BD",
                                activebackground="#ADB5BD")

    # ── Tarjeta de resultado ─────────────────────────────────────────
    def _actualizar_card(self, c_obj, maximizar):
        res = self.resultado
        if not res["exito"]:
            msg = res.get("mensaje", "Error")
            self.card.config(bg="#FFF3CD")
            self.lbl_card_titulo.config(bg="#FFF3CD", fg="#856404",
                                        text="\u26a0  Sin solución óptima")
            self.lbl_card_valor.config( bg="#FFF3CD", fg="#856404", text=msg[:60])
            self.lbl_card_punto.config( bg="#FFF3CD", text="")
        else:
            tipo = "Máximo" if maximizar else "Mínimo"
            x = res["x_opt"]
            z = res["z_opt"]
            self.card.config(bg="#D1E7DD")
            self.lbl_card_titulo.config(bg="#D1E7DD", fg="#0A3622",
                                        text=f"\u2714  {tipo} global encontrado")
            self.lbl_card_valor.config( bg="#D1E7DD", fg="#0A3622",
                                        text=f"Z* = {z:.4f}")
            self.lbl_card_punto.config( bg="#D1E7DD", fg="#146C43",
                                        text=f"Punto óptimo:  X\u2081 = {float(x[0]):.4f}  |  X\u2082 = {float(x[1]):.4f}")

    # ── Consola de detalle ───────────────────────────────────────────
    def _w(self, text, tag="ok"):
        self.txt_resultados.insert(tk.END, text, tag)

    def _mostrar_detalle(self, c_obj, maximizar):
        t = self.txt_resultados
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)

        sep = "\u2500" * 44 + "\n"
        tipo = "Maximización" if maximizar else "Minimización"
        self._w(sep, "sep")
        self._w(f"  {tipo}  \u2014  {datetime.now().strftime('%H:%M:%S')}\n", "info")
        self._w(f"  Z = {self._fmt(c_obj[0])}\u00b7X\u2081 + {self._fmt(c_obj[1])}\u00b7X\u2082\n", "info")
        self._w(sep, "sep")

        res = self.resultado
        if not res["exito"]:
            self._w(f"\n  \u26a0  {res['mensaje']}\n", "error")
            t.config(state=tk.DISABLED)
            return

        self._w("\n  Vértices factibles:\n", "info")
        for i, v in enumerate(res["vertices"], 1):
            z = c_obj[0] * float(v[0]) + c_obj[1] * float(v[1])
            self._w(f"    V{i}: ({float(v[0]):.3f}, {float(v[1]):.3f})  \u2192  Z = {z:.4f}\n")

        x = res["x_opt"]
        self._w("\n" + sep, "sep")
        self._w(f"  \u2714  ÓPTIMO: ({float(x[0]):.4f}, {float(x[1]):.4f})\n", "optimo")
        self._w(f"     Z*  =  {res['z_opt']:.4f}\n", "optimo")
        self._w(sep, "sep")
        t.config(state=tk.DISABLED)

    # ── Exportar PDF ─────────────────────────────────────────────────
    def _exportar_pdf(self):
        if self.resultado is None:
            messagebox.showwarning("Sin datos", "Primero resuelve un problema.")
            return

        try:
            c1 = float(self.ent_z1.get())
            c2 = float(self.ent_z2.get())
        except ValueError:
            c1 = c2 = 0.0

        restricciones_pdf = [
            {"a": r["a"][0], "b": r["a"][1], "signo": r["tipo"], "c": r["b"], "no_neg": False}
            for r in self._restricciones
        ]

        vertices = [tuple(float(x) for x in v) for v in self.resultado.get("vertices", [])]
        x_opt    = self.resultado.get("x_opt")
        optimo   = tuple(float(x) for x in x_opt) if x_opt is not None else None
        z_opt    = self.resultado.get("z_opt")

        if not self.resultado["exito"]:
            msg = self.resultado.get("mensaje", "")
            tipo_sol = "infactible" if "INFACTIBLE" in msg else "ilimitado"
        else:
            if z_opt is not None and vertices:
                z_vals = [c1 * v[0] + c2 * v[1] for v in vertices]
                conteo = sum(1 for z in z_vals if abs(z - z_opt) < 1e-8)
                tipo_sol = "multiple" if conteo > 1 else "unica"
            else:
                tipo_sol = "unica"

        datos = {
            "tipo_problema": self.tipo_var.get(), "z_coef_a": c1, "z_coef_b": c2,
            "restricciones": restricciones_pdf, "intersecciones": [],
            "vertices": vertices, "optimo": optimo,
            "valor_optimo": float(z_opt) if z_opt is not None else None,
            "tipo_solucion": tipo_sol, "ruta_grafica": self.ruta_grafica,
        }

        try:
            ruta = self.exportador.generar(datos)
            messagebox.showinfo("PDF generado", f"Reporte guardado en:\n{ruta}")
            self._set_estado(f"\u2714 PDF exportado: {os.path.basename(ruta)}")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    # ── Limpiar ──────────────────────────────────────────────────────
    def _limpiar(self):
        self._restricciones.clear()
        self.resultado    = None
        self.ruta_grafica = ""

        for w in (self.ent_z1, self.ent_z2, self.ent_a1, self.ent_a2, self.ent_b):
            w.delete(0, tk.END)

        self.lista_rest.delete(0, tk.END)

        self.txt_resultados.config(state=tk.NORMAL)
        self.txt_resultados.delete("1.0", tk.END)
        self.txt_resultados.config(state=tk.DISABLED)

        # Resetear tarjeta
        self.card.config(bg=COLORS["border_light"])
        self.lbl_card_titulo.config(bg=COLORS["border_light"], fg=COLORS["text_muted"],
                                     text="Sin resolver")
        self.lbl_card_valor.config(bg=COLORS["border_light"], fg=COLORS["text_muted"], text="—")
        self.lbl_card_punto.config(bg=COLORS["border_light"], fg=COLORS["text_muted"], text="")

        self.panel_grafico.limpiar()
        self._habilitar_pdf(False)
        self._set_estado("Todo limpiado. Listo para comenzar.")

    # ── Estado ───────────────────────────────────────────────────────
    def _set_estado(self, msg):
        self.lbl_estado.config(text=f"  {msg}")

    # ── Formateo ─────────────────────────────────────────────────────
    @staticmethod
    def _fmt(num: float) -> str:
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}"
