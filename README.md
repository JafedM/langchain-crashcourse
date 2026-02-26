# Introducción a Agentes de IA con LangChain y LangSmith

Este repositorio contiene el material práctico para el taller intensivo de 3 horas impartido a los estudiantes de la Maestría en Computación del CIMAT.

## Objetivo
Aprender a diseñar, construir y monitorear Agentes de Inteligencia Artificial utilizando el ecosistema de LangChain. Pasaremos de la teoría interactiva en Jupyter Notebooks a un despliegue de un agente productivo con observabilidad en LangSmith.

## Requisitos Previos
- Python 3.9 o superior.
- Clave de API de OpenAI (o proveedor asignado).
- Cuenta gratuita en [LangSmith](https://smith.langchain.com/).

## Instrucciones de Instalación

**1. Clonar el repositorio:**
```bash
git clone https://github.com/JafedM/langchain-crashcourse.git
cd langchain-crashcourse
```

**2. Crear y activar un entorno virtual:**
```bash
# En Windows:
python -m venv .venv
venv\Scripts\activate

# En macOS/Linux:
python3 -m venv .venv
source venv/bin/activate
```

**3. Instalar las dependencias:**
```bash
pip install -r requirements.txt
```

**4. Configurar variables de entorno:**
Duplica el archivo `.env.example`, renómbralo a `.env` y agrega tus claves de API correspondientes.

## Estructura del Taller
- `/notebooks`: Exploración paso a paso de Prompts, Tools y memoria del agente.

- `/app`: Código final del agente empaquetado como una aplicación lista para ser monitoreada en LangSmith.

## Pruebas Locales con LangGraph Studio (`langgraph dev`)

Para visualizar y depurar el flujo del agente de forma interactiva en tu navegador, utilizaremos el servidor local de LangGraph.

**1. Instalar el CLI de LangGraph:**
Asegúrate de tener instalado el CLI en tu entorno virtual (si no se instaló con los requirements):
```bash
pip install -U "langgraph-cli[inmem]"
```
**2. Iniciar el servidor de desarrollo:**
Desde la raíz del proyecto, ejecuta:

```bash
langgraph dev
```

**3. Interactuar con el Agente:**
El comando anterior abrirá automáticamente LangGraph Studio en tu navegador (usualmente en http://localhost:8123). Desde ahí podrás enviar mensajes al agente, visualizar el grafo de ejecución paso a paso, modificar el estado en tiempo real y ver exactamente qué herramientas está llamando y con qué argumentos.
