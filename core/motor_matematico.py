"""
Capa de lógica matemática.
Resuelve el problema de PL y calcula los vértices de la región factible.
"""

import numpy as np
from scipy.optimize import linprog


class MotorMatematico:
    """
    Resuelve problemas de Programación Lineal con dos variables
    usando scipy.optimize.linprog y calcula los vértices factibles.
    """

    def __init__(self):
        self.resultado = None
        self.vertices = []

    # ------------------------------------------------------------------
    def resolver(self, c_obj, A_ub, b_ub, A_eq, b_eq, maximizar):
        """
        Resuelve el problema y devuelve un diccionario con:
            exito, mensaje, x_opt, z_opt, vertices, maximizar
        """
        self.resultado = None
        self.vertices = []

        c_linprog = [-ci for ci in c_obj] if maximizar else list(c_obj)
        bounds = [(0, None), (0, None)]

        A_ub_np = np.array(A_ub, dtype=float) if A_ub else None
        b_ub_np = np.array(b_ub, dtype=float) if b_ub else None
        A_eq_np = np.array(A_eq, dtype=float) if A_eq else None
        b_eq_np = np.array(b_eq, dtype=float) if b_eq else None

        try:
            res = linprog(
                c=c_linprog,
                A_ub=A_ub_np, b_ub=b_ub_np,
                A_eq=A_eq_np, b_eq=b_eq_np,
                bounds=bounds,
                method="highs",
            )
        except Exception as e:
            return {
                "exito": False,
                "mensaje": f"Error en solver: {e}",
                "x_opt": None,
                "z_opt": None,
                "vertices": [],
            }

        if res.status == 0:
            x_opt = res.x
            z_opt = sum(ci * xi for ci, xi in zip(c_obj, x_opt))
            vertices = self._calcular_vertices(A_ub, b_ub, A_eq, b_eq)
            self.vertices = vertices
            self.resultado = {
                "exito": True,
                "mensaje": "Solución óptima encontrada.",
                "x_opt": x_opt,
                "z_opt": z_opt,
                "vertices": vertices,
                "maximizar": maximizar,
            }
        elif res.status == 2:
            self.resultado = {
                "exito": False,
                "vertices": [],
                "mensaje": "INFACTIBLE: No existe región factible con esas restricciones.",
                "x_opt": None,
                "z_opt": None,
            }
        elif res.status == 3:
            self.resultado = {
                "exito": False,
                "vertices": [],
                "mensaje": "NO ACOTADO: La región factible se extiende al infinito.",
                "x_opt": None,
                "z_opt": None,
            }
        else:
            self.resultado = {
                "exito": False,
                "vertices": [],
                "mensaje": f"Estado {res.status}: {res.message}",
                "x_opt": None,
                "z_opt": None,
            }

        return self.resultado

    # ------------------------------------------------------------------
    def _calcular_vertices(self, A_ub, b_ub, A_eq, b_eq):
        """Calcula los vértices de la región factible por intersección de pares de hiperplanos."""
        lineas = [
            (np.array([1.0, 0.0]), 0.0),
            (np.array([0.0, 1.0]), 0.0),
        ]
        if A_ub:
            for a, b in zip(A_ub, b_ub):
                lineas.append((np.array(a, dtype=float), float(b)))
        if A_eq:
            for a, b in zip(A_eq, b_eq):
                lineas.append((np.array(a, dtype=float), float(b)))

        candidatos = []
        for i in range(len(lineas)):
            for j in range(i + 1, len(lineas)):
                A_s = np.array([lineas[i][0], lineas[j][0]])
                b_s = np.array([lineas[i][1], lineas[j][1]])
                try:
                    if abs(np.linalg.det(A_s)) < 1e-10:
                        continue
                    pt = np.linalg.solve(A_s, b_s)
                    if pt[0] >= -1e-8 and pt[1] >= -1e-8:
                        candidatos.append(
                            np.array([max(0.0, pt[0]), max(0.0, pt[1])])
                        )
                except np.linalg.LinAlgError:
                    continue

        validos = []
        for pt in candidatos:
            ok = True
            if A_ub:
                for a, b in zip(A_ub, b_ub):
                    if np.dot(a, pt) > b + 1e-6:
                        ok = False
                        break
            if ok and A_eq:
                for a, b in zip(A_eq, b_eq):
                    if abs(np.dot(a, pt) - b) > 1e-6:
                        ok = False
                        break
            if ok:
                validos.append(pt)

        # Eliminar duplicados
        unicos = []
        for v in validos:
            if not any(np.linalg.norm(v - u) < 1e-6 for u in unicos):
                unicos.append(v)
        return unicos

    # ------------------------------------------------------------------
    def evaluar_vertices(self, c_obj, vertices):
        """Devuelve lista de (vertice, valor_z) para cada vértice."""
        return [
            (v, sum(ci * xi for ci, xi in zip(c_obj, v)))
            for v in vertices
        ]
