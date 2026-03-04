import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Cargar variables de entorno (API Keys de OpenAI y LangSmith)
load_dotenv()

from app.agent import graph

def chat_interactivo():
    print("="*50)
    print("🤖 Asistente Corporativo (CIMAT 2026)")
    print("Escribe 'salir' o 'quit' para terminar la conversación.")
    print("="*50)
    
    # LangGraph usa un 'thread_id' para mantener la memoria de la conversación
    # si implementamos persistencia. Por ahora, creamos uno único por sesión.
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    while True:
        user_input = input("\n🧑 Tú: ")
        
        if user_input.lower() in ['salir', 'quit', 'exit']:
            print("👋 ¡Hasta luego!")
            break
            
        if not user_input.strip():
            continue

        # Formateamos la entrada del usuario como un HumanMessage
        mensaje = HumanMessage(content=user_input)
        
        print("\n🧠 Pensando...\n")
        
        # Usamos .stream() en lugar de .invoke() para ver el proceso paso a paso
        # Esto nos permite ver cómo el flujo salta entre el 'agent' y las 'tools'
        try:
            for event in graph.stream({"messages": [mensaje]}, config, stream_mode="updates"):
                for node_name, node_state in event.items():
                    print(f"--- [Nodo ejecutado: {node_name}] ---")
                    
                    # Obtenemos el último mensaje generado por este nodo
                    ultimo_mensaje = node_state["messages"][-1]
                    
                    # Si el nodo es el agente y generó una llamada a herramienta:
                    if node_name == "agent" and hasattr(ultimo_mensaje, "tool_calls") and ultimo_mensaje.tool_calls:
                        for tool_call in ultimo_mensaje.tool_calls:
                            print(f"🔧 Herramienta solicitada: {tool_call['name']}")
                            print(f"📥 Argumentos: {tool_call['args']}")
                            
                    # Si el nodo es el agente y dio una respuesta final (texto):
                    elif node_name == "agent" and ultimo_mensaje.content:
                        print(f"\n🤖 Agente: {ultimo_mensaje.content}\n")
                        
                    # Si el nodo son las herramientas, mostramos el resultado crudo:
                    elif node_name == "tools":
                        print(f"📤 Resultado de la herramienta: {ultimo_mensaje.content[:150]}...\n")
                        
        except Exception as e:
            print(f"\n❌ Ocurrió un error en la ejecución: {e}")

if __name__ == "__main__":
    import os
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  ADVERTENCIA: No se encontró GOOGLE_API_KEY en las variables de entorno.")
        print("Por favor, configura tu archivo .env antes de continuar.")
    else:
        chat_interactivo()