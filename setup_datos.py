# setup_datos.py
import sqlite3
import json
from datetime import datetime, timedelta

def configurar_base_datos():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    
    # Tabla 1: Productos (La que ya teníamos)
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                      (id INTEGER PRIMARY KEY, nombre TEXT, categoria TEXT, precio REAL, stock INTEGER)''')
    productos = [('Laptop Pro', 'Electrónica', 1200.0, 10), ('Monitor 27"', 'Electrónica', 300.0, 25),
                 ('Silla Ergonómica', 'Oficina', 150.00, 15), ('Escritorio', 'Oficina', 200.00, 5)]
    cursor.executemany('INSERT INTO productos (nombre, categoria, precio, stock) VALUES (?, ?, ?, ?)', productos)
    
    # Tabla 2: Clientes (Nueva para el ejercicio)
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes 
                      (id INTEGER PRIMARY KEY, nombre TEXT, empresa TEXT, email TEXT, telefono TEXT)''')
    clientes = [
        ('Ana Lopez', 'TechCorp', 'ana@techcorp.com', '555-0101'),
        ('Carlos Ruiz', 'Soluciones Globales', 'carlos@sglobal.com', '555-0202'),
        ('Carlos Slim', 'Telmex', 'carlos@telmex.com', '555-9999'), # ¡El gemelo de nombre!
        ('Maria Gomez', 'Innovación SA', 'maria@innovacion.mx', '555-0303')
    ]
    cursor.executemany('INSERT INTO clientes (nombre, empresa, email, telefono) VALUES (?, ?, ?, ?)', clientes)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos 'inventario.db' creada.")

def configurar_agenda():
    hoy = datetime.now()
    eventos = [
        {
            "titulo": "Revisión de Avances de Tesis",
            "fecha_hora": (hoy + timedelta(days=1)).strftime("%Y-%m-%d 10:00"),
            "descripcion": "Revisión del capítulo 2 con el asesor."
        },
        {
            "titulo": "Comida con el equipo",
            "fecha_hora": (hoy + timedelta(days=1)).strftime("%Y-%m-%d 14:00"),
            "descripcion": "Comida de integración en la cafetería."
        },
        {
            "titulo": "Clase de Sistemas Distribuidos",
            "fecha_hora": (hoy + timedelta(days=2)).strftime("%Y-%m-%d 09:00"),
            "descripcion": "Entrega de la práctica 3."
        }
    ]
    
    with open("agenda.json", "w") as f:
        json.dump(eventos, f, indent=4)
    print("✅ Archivo 'agenda.json' creado con eventos de prueba.")

if __name__ == "__main__":
    configurar_base_datos()
    configurar_agenda()