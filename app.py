import os
from flask import Flask, jsonify
# Importamos tu lógica matemática
from centro.motor_matematico import Motormatematico 

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Servidor de Programación Lineal Activo! Conectando interfaz..."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
