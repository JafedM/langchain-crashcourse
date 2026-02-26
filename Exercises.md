**Reto 1: Herramienta de Contacto de Clientes (Base de Datos)**
El Problema: El agente necesita poder buscar la información de contacto de los clientes dentro de los sistemas de automatización de fuerza de ventas (SFA) de la empresa para poder mandarles correos o llamarles.

La Tarea: Crear una herramienta llamada buscar_cliente que reciba el nombre de un cliente (ej. "Ana") y haga un SELECT en la tabla clientes de inventario.db.

Lo que aprenderán: A definir los argumentos de entrada en el docstring para que el LLM sepa que debe extraer el nombre de la persona a partir del prompt del usuario y pasarlo a la consulta SQL usando LIKE.

**Reto 2: Resumen del Día (Lectura de JSON)**
El Problema: La herramienta que ya tenemos (agendar_reunion) solo escribe en la agenda, pero el agente no tiene forma de saber qué hay programado para un día específico si el usuario se lo pregunta.

La Tarea: Crear una herramienta llamada consultar_agenda_dia que reciba una fecha en formato YYYY-MM-DD. La herramienta debe abrir agenda.json, iterar sobre la lista de diccionarios, filtrar los que coincidan con la fecha solicitada y devolver un string formateado con el resumen de ese día.

Lo que aprenderán: A manejar tipos de datos (el LLM debe generar la fecha exacta basándose en el contexto del día actual) y a devolver la información estructurada de vuelta al LLM para que este redacte una respuesta natural.