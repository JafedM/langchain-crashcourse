from typing import Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

# Importamos las herramientas que creamos en el paso anterior
from app.tools import (
    consultar_inventario,
    obtener_precio_accion,
    agendar_reunion,
    buscar_cliente,
    consultar_agenda_dia
)

# ==========================================
# 1. Configuración de Herramientas y LLM
# ==========================================
# Agrupamos todas las herramientas en una lista
tools = [
    consultar_inventario, 
    obtener_precio_accion, 
    agendar_reunion, 
    buscar_cliente, 
    consultar_agenda_dia
]

# Inicializamos el modelo (usamos gpt-4o-mini por ser rápido y económico)
# temperature=0 es crucial para que el agente sea determinista al usar herramientas
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# "Conectamos" las herramientas al modelo. Esto inyecta los esquemas de las 
# funciones (docstrings y argumentos) en la API del LLM para que sepa que existen.
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 2. Definición de los Nodos del Grafo
# ==========================================

def chatbot_node(state: MessagesState):
    """
    Este nodo es el 'Cerebro'. Toma el historial de mensajes actual, 
    le añade instrucciones de sistema y le pide al LLM que decida el siguiente paso.
    """
    mensajes = [
        SystemMessage(content="""Eres un asistente corporativo altamente eficiente. 
        Tienes acceso a bases de datos de inventario, clientes, y herramientas de agenda.
        Usa las herramientas a tu disposición para responder a las solicitudes del usuario.
        Si no sabes la respuesta o la herramienta falla, admítelo y pide aclaraciones.
        La fecha actual es 26 de febrero de 2026.""")
    ] + state["messages"]
    
    # Invocamos al modelo
    response = llm_with_tools.invoke(mensajes)
    
    # Devolvemos el nuevo mensaje generado (LangGraph lo agregará a la lista automáticamente)
    return {"messages": [response]}

# LangGraph prebuilt tiene un ToolNode que se encarga automáticamente de 
# ejecutar la función de Python correspondiente cuando el LLM lo solicita.
tool_node = ToolNode(tools=tools)

# ==========================================
# 3. Construcción del Grafo (El Flujo)
# ==========================================

# Usamos MessagesState, que es un estado predefinido que solo contiene 
# una lista de mensajes (ideal para agentes conversacionales).
workflow = StateGraph(MessagesState)

# Agregamos nuestros dos nodos principales
workflow.add_node("agent", chatbot_node)
workflow.add_node("tools", tool_node)

# Definimos las conexiones (Edges)
# Empezamos siempre en el nodo del agente
workflow.add_edge(START, "agent")

# Aquí está la magia condicional:
# tools_condition revisa si la respuesta del LLM tiene "tool_calls".
# Si TIENE tool_calls -> Va al nodo "tools"
# Si NO TIENE tool_calls (solo texto) -> Va al nodo "END" y termina la ejecución.
workflow.add_conditional_edges("agent", tools_condition)

# Una vez que la herramienta termina de ejecutarse, SIEMPRE regresamos al agente
# para que evalúe el resultado de la herramienta y decida si ya puede responder.
workflow.add_edge("tools", "agent")

# ==========================================
# 4. Compilación
# ==========================================
# La variable DEBE llamarse 'graph' para que langgraph.json la encuentre.
graph = workflow.compile()