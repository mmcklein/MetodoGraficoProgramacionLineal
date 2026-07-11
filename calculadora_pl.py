"""
GraphLP — Punto de entrada de la aplicación.

Estructura por capas:
  graphlp_config/  → colores y fuentes
  core/            → motor matemático + exportador PDF
  ui/              → interfaz gráfica + panel de gráfica
"""

import sys
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

os.chdir(_BASE)

from ui.app import AppGraphLP

if __name__ == "__main__":
    AppGraphLP()
