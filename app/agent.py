from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from datetime import datetime

# Nombres de herramientas de agenda para enrutar
AGENDA_TOOL_NAMES = {"consultar_agenda_dia", "agendar_reunion"}

# Importamos las herramientas que creamos en el paso anterior
from app.tools import (
    consultar_inventario,
    obtener_precio_accion,
    agendar_reunion,
    buscar_cliente,
    consultar_agenda_dia,
    consultar_tabla_bd,
)

# ==========================================
# 1. Configuración de Herramientas y LLM
# ==========================================
# Herramientas del nodo principal (cliente, precio, inventario)
tools_main = [buscar_cliente, obtener_precio_accion, consultar_inventario, consultar_tabla_bd]
# Herramientas del nodo de agenda
tools_agenda = [consultar_agenda_dia, agendar_reunion]
# Todas para que el LLM pueda decidir cuál usar
tools = tools_main + tools_agenda

# Inicializamos el modelo (usamos gpt-4.1-nano por ser rápido y económico)
# temperature=0 es crucial para que el agente sea determinista al usar herramientas
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

# "Conectamos" las herramientas al modelo. Esto inyecta los esquemas de las 
# funciones (docstrings y argumentos) en la API del LLM para que sepa que existen.
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# ==========================================
# 2. Definición de los Nodos del Grafo
# ==========================================

def chatbot_node(state: MessagesState):
    """
    Este nodo es el 'Cerebro'. Toma el historial de mensajes actual, 
    le añade instrucciones de sistema y le pide al LLM que decida el siguiente paso.
    """
    fecha_hoy = datetime.now().strftime("%d de %B de %Y")
    mensajes = [
        SystemMessage(content=f"""Eres un asistente corporativo altamente eficiente. 
        Tienes acceso a bases de datos de inventario, clientes, y herramientas de agenda.
        Usa las herramientas a tu disposición para responder a las solicitudes del usuario.
        Si no sabes la respuesta o la herramienta falla, admítelo y pide aclaraciones.
        La fecha actual es {fecha_hoy}.""")
    ] + state["messages"]
    
    # Invocamos al modelo
    response = llm_with_tools.invoke(mensajes)
    
    # Devolvemos el nuevo mensaje generado (LangGraph lo agregará a la lista automáticamente)
    return {"messages": [response]}

# Nodo de herramientas principales (cliente, precio, inventario)
tool_node = ToolNode(tools=tools_main)
# Nodo de herramientas de agenda
agenda_tool_node = ToolNode(tools=tools_agenda)

# ==========================================
# 3. Construcción del Grafo (El Flujo)
# ==========================================

def route_after_agent(state: MessagesState):
    """
    Decide a qué nodo ir después del agente:
    - Si el LLM no pidió ninguna herramienta -> terminar (END).
    - Si pidió consultar_agenda_dia o agendar_reunion -> nodo "agenda_tools".
    - Si pidió otra herramienta (cliente, precio, inventario) -> nodo "sql_tools".
    """
    ultimo_mensaje = state["messages"][-1]
    herramientas_solicitadas = getattr(ultimo_mensaje, "tool_calls", None)

    # Si no hay tool_calls, el agente ya respondió con texto -> terminar
    if not herramientas_solicitadas:
        return END

    # Ver qué herramientas pidió el LLM (por nombre)
    nombres_herramientas = {llamada["name"] for llamada in ultimo_mensaje.tool_calls}

    # Si alguna herramienta solicitada es de agenda -> ir a "agenda_tools"
    # Si no (cliente, precio, inventario) -> ir a "sql_tools"
    alguna_es_de_agenda = any(
        nombre in AGENDA_TOOL_NAMES for nombre in nombres_herramientas
    )
    if alguna_es_de_agenda:
        return "agenda_tools"
    return "sql_tools"

# Usamos MessagesState, que es un estado predefinido que solo contiene 
# una lista de mensajes (ideal para agentes conversacionales).
workflow = StateGraph(MessagesState)

# Agregamos el nodo del agente y los dos nodos de herramientas
workflow.add_node("agent", chatbot_node)
workflow.add_node("sql_tools", tool_node)
workflow.add_node("agenda_tools", agenda_tool_node)

# Definimos las conexiones (Edges)
# Empezamos siempre en el nodo del agente
workflow.add_edge(START, "agent")

# Arista condicional: según los tool_calls, ir a "sql_tools", "agenda_tools" o END
workflow.add_conditional_edges("agent", route_after_agent,
                               {
        "sql_tools": "sql_tools",
        "agenda_tools": "agenda_tools",
        END: END
    })

# Tras ejecutar herramientas, siempre volvemos al agente
workflow.add_edge("sql_tools", "agent")
workflow.add_edge("agenda_tools", "agent")

# ==========================================
# 4. Compilación
# ==========================================
# La variable DEBE llamarse 'graph' para que langgraph.json la encuentre.
graph = workflow.compile()