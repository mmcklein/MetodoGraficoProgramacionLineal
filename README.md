# 📊 GraphLP - Método Gráfico de Programación Lineal

**GraphLP** es una aplicación de escritorio desarrollada en Python para resolver problemas de **Programación Lineal con dos variables** mediante el **método gráfico**. Diseñada para estudiantes y profesionales de Investigación de Operaciones.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Características

- ✅ **Interfaz gráfica intuitiva** con Tkinter (mejorada para UX)
- ✅ **Resolución automática** de problemas de maximización y minimización
- ✅ **Visualización gráfica** de la región factible, vértices y punto óptimo
- ✅ **Exportación a PDF** con reporte profesional y gráficas
- ✅ **Ejemplos precargados** listos para probar
- ✅ **Cálculo de vértices** mediante intersección de restricciones
- ✅ **Arquitectura por capas** (config, core, ui)
- ✅ **Compatible** con Python 3.9+ y Linux/Windows

---

## 🚀 Instalación

### Requisitos previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Fedora/RHEL

```bash
# Instalar dependencias del sistema
sudo dnf install python3 python3-pip python3-tkinter \
                 python3-numpy python3-scipy python3-pillow python3-pillow-tk \
                 python3-matplotlib python3-reportlab

# Clonar el repositorio
git clone https://github.com/TU_USUARIO/graphlp.git
cd graphlp
```

### Ubuntu/Debian

```bash
# Instalar dependencias
sudo apt update
sudo apt install python3 python3-pip python3-tk \
                 python3-numpy python3-scipy python3-pil python3-pil.imagetk \
                 python3-matplotlib python3-reportlab

# Clonar el repositorio
git clone https://github.com/TU_USUARIO/graphlp.git
cd graphlp
```

### Windows

```bash
# Instalar con pip (requiere Python 3.9+)
pip install numpy scipy pillow matplotlib reportlab

# Clonar el repositorio
git clone https://github.com/TU_USUARIO/graphlp.git
cd graphlp
```

---

## 📖 Uso

### Ejecutar la aplicación

```bash
cd app
python3 calculadora_pl.py
```

### Ejemplo básico

1. **Selecciona el tipo de problema**: Maximizar o Minimizar
2. **Ingresa la función objetivo**:
   - Ejemplo: `Z = 5X₁ + 4X₂`
3. **Agrega restricciones**:
   - Ejemplo: `6X₁ + 4X₂ ≤ 24`
   - Ejemplo: `1X₁ + 2X₂ ≤ 6`
4. **Haz clic en "Resolver"**
5. **Visualiza** la gráfica y el resultado óptimo
6. **Exporta a PDF** si lo necesitas

### Cargar ejemplos

Haz clic en **"💡 Cargar ejemplo"** y selecciona uno de los problemas predefinidos:
- Maximizar ganancias
- Minimizar costos
- Producción mixta

---

## 🏗️ Arquitectura

El proyecto está organizado en capas:

```
app/
├── calculadora_pl.py          # Punto de entrada
├── graphlp_config/            # Configuración (colores, fuentes)
│   ├── __init__.py
│   ├── colores.py
│   └── fuentes.py
├── core/                      # Lógica de negocio
│   ├── __init__.py
│   ├── motor_matematico.py   # Solver (scipy.optimize.linprog)
│   └── exportador_pdf.py     # Generación de reportes
└── ui/                        # Interfaz de usuario
    ├── __init__.py
    ├── app.py                 # Ventana principal
    └── panel_grafico.py       # Widget matplotlib
```

### Tecnologías utilizadas

- **Tkinter**: Interfaz gráfica
- **NumPy**: Cálculo numérico
- **SciPy**: Solver de programación lineal (`linprog`)
- **Matplotlib**: Visualización de gráficas
- **ReportLab**: Generación de PDFs
- **Pillow**: Procesamiento de imágenes

---

## 🎨 Capturas de pantalla

_Próximamente: agregar capturas de la interfaz_

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Sube los cambios (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 👤 Autor

**Tu Nombre**  
GitHub: [@TU_USUARIO](https://github.com/TU_USUARIO)

---

## 📚 Referencias

- [Programación Lineal - Wikipedia](https://es.wikipedia.org/wiki/Programaci%C3%B3n_lineal)
- [Scipy linprog documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html)
- [Tkinter documentation](https://docs.python.org/3/library/tkinter.html)

---

⭐ **Si te resultó útil, deja una estrella en el repositorio** ⭐
