import sqlite3
import json
import os
from datetime import datetime
from langchain_core.tools import tool

# ==========================================
# TOOL 1: Consulta a Base de Datos (SQLite)
# ==========================================
@tool
def consultar_inventario(categoria: str) -> str:
    """
    Consulta la base de datos SQL local de la empresa para buscar productos.
    Útil para saber qué artículos están disponibles, su stock y precios.
    Args:
        categoria (str): La categoría del producto (ej. 'Electrónica', 'Oficina').
    """
    db_path = "inventario.db"
    
    # Validar si la base de datos existe; si no, avisar al agente
    if not os.path.exists(db_path):
        return "Error: La base de datos no existe. Por favor, ejecuta el script de configuración primero."
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Consulta real a la base de datos
        cursor.execute("SELECT nombre, precio, stock FROM productos WHERE categoria = ?", (categoria,))
        resultados = cursor.fetchall()
        conn.close()
        
        if not resultados:
            return f"No se encontraron productos en la categoría: {categoria}."
        
        respuesta = f"Productos en {categoria}:\n"
        for nombre, precio, stock in resultados:
            respuesta += f"- {nombre}: ${precio} (Stock: {stock})\n"
        return respuesta
    
    except sqlite3.Error as e:
        return f"Error al consultar la base de datos: {str(e)}"

# ==========================================
# TOOL 2: API Externa (Simulada)
# ==========================================
@tool
def obtener_precio_accion(ticker: str) -> str:
    """
    Obtiene el precio actual de una acción en la bolsa de valores consultando una API.
    Útil para responder preguntas sobre el mercado financiero.
    Args:
        ticker (str): El símbolo de la acción (ej. 'AAPL', 'AMZN', 'NFLX', 'NVDA').
    """
    # Simulamos una llamada a una API financiera (como yfinance o Alpha Vantage)
    # En un entorno real, aquí usarías requests.get("url_de_la_api...")
    precios_mock = {
        "AAPL": 185.50,
        "AMZN": 170.20,
        "NFLX": 605.10,
        "NVDA": 850.30,
        "KOF": 160.00,
        "BBVA": 9.50
    }
    
    ticker = ticker.upper()
    if ticker in precios_mock:
        return f"El precio actual de {ticker} es de ${precios_mock[ticker]} USD."
    else:
        return f"No se pudo obtener el precio para el ticker {ticker}. API no retornó datos."

# ==========================================
# TOOL 3: Escritura/Agendamiento (Sistema de Archivos)
# ==========================================
@tool
def agendar_reunion(titulo: str, fecha_hora: str, descripcion: str) -> str:
    """
    Agenda una nueva reunión o evento guardándolo en el calendario del sistema.
    Args:
        titulo (str): El título de la reunión.
        fecha_hora (str): La fecha y hora en formato 'YYYY-MM-DD HH:MM'.
        descripcion (str): Breve descripción o propósito de la reunión.
    """
    archivo_agenda = "agenda.json"
    nuevo_evento = {
        "titulo": titulo,
        "fecha_hora": fecha_hora,
        "descripcion": descripcion,
        "creado_en": datetime.now().isoformat()
    }
    
    eventos = []
    # Leer eventos existentes si el archivo ya existe
    if os.path.exists(archivo_agenda):
        with open(archivo_agenda, "r") as f:
            try:
                eventos = json.load(f)
            except json.JSONDecodeError:
                pass
                
    eventos.append(nuevo_evento)
    
    with open(archivo_agenda, "w") as f:
        json.dump(eventos, f, indent=4)
        
    return f"✅ Reunión '{titulo}' agendada exitosamente para el {fecha_hora}."

import sqlite3
import json
import os
from langchain_core.tools import tool

# ==========================================
# RETO 1: Búsqueda en Base de Datos (SFA)
# ==========================================
@tool
def buscar_cliente(nombre: str) -> str:
    """
    Busca la información de contacto de un cliente en el sistema CRM/SFA de la empresa.
    Útil cuando necesitas obtener el correo electrónico, teléfono o la empresa de un cliente.
    
    Args:
        nombre (str): El nombre o apellido del cliente a buscar (ej. 'Ana', 'Carlos').
    """
    db_path = "inventario.db"
    
    if not os.path.exists(db_path):
        return "Error: La base de datos de clientes no está disponible."
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Usamos LIKE para que encuentre coincidencias parciales (ej. "Ana" encuentra "Ana Lopez")
        cursor.execute("SELECT nombre, empresa, email, telefono FROM clientes WHERE nombre LIKE ?", (f"%{nombre}%",))
        resultados = cursor.fetchall()
        conn.close()
        
        if not resultados:
            return f"No se encontró ningún cliente que coincida con el nombre: {nombre}."
            
        respuesta = f"Resultados de la búsqueda para '{nombre}':\n"
        for row in resultados:
            respuesta += f"- Nombre: {row[0]} | Empresa: {row[1]} | Email: {row[2]} | Tel: {row[3]}\n"
            
        return respuesta
        
    except sqlite3.Error as e:
        return f"Error en la base de datos al buscar el cliente: {str(e)}"

# ==========================================
# RETO 2: Lectura de JSON y Filtrado
# ==========================================
@tool
def consultar_agenda_dia(fecha: str) -> str:
    """
    Consulta los eventos y reuniones programadas en la agenda para un día específico.
    
    Args:
        fecha (str): La fecha exacta a consultar estrictamente en formato 'YYYY-MM-DD'.
    """
    archivo_agenda = "agenda.json"
    
    if not os.path.exists(archivo_agenda):
        return "La agenda está vacía o el archivo no existe."
        
    try:
        with open(archivo_agenda, "r") as f:
            eventos = json.load(f)
            
        # Filtramos los eventos donde la cadena 'fecha_hora' comience con la fecha solicitada
        eventos_del_dia = [e for e in eventos if e.get("fecha_hora", "").startswith(fecha)]
        
        if not eventos_del_dia:
            return f"No tienes ningún evento programado para el {fecha}."
            
        respuesta = f"Agenda para el {fecha}:\n"
        for evento in eventos_del_dia:
            hora = evento["fecha_hora"].split(" ")[1] # Extraemos solo la hora
            respuesta += f"- [{hora}] {evento['titulo']}: {evento['descripcion']}\n"
            
        return respuesta
        
    except json.JSONDecodeError:
        return "Error: El archivo de la agenda está corrupto o tiene un formato inválido."
    except Exception as e:
        return f"Error inesperado al leer la agenda: {str(e)}"