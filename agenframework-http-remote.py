import logging
import os
from datetime import datetime
from rich.logging import RichHandler
from agent_framework.openai import OpenAIChatClient
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from fastapi import FastAPI
import asyncio
import anyio

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("agentframework-http-remote")
logger.setLevel(logging.INFO)

app = FastAPI()
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://facel-soporte-ia.fastmcp.app/mcp")
API_HOST = os.getenv("API_HOST", "ollama")
access_token = "fmcp_xpmxheUukEZfauKWNHUY0RvFN5fZh8GICBicJOXb6i0"

# Configure constants and client based on environment
RUNNING_IN_PRODUCTION = os.getenv("RUNNING_IN_PRODUCTION", "false").lower() == "true"

client = OpenAIChatClient(
            base_url=os.environ.get("OLLAMA_ENDPOINT", "http://127.0.0.1:11434/v1"),
            api_key="none",
            model_id=os.environ.get("OLLAMA_MODEL", "mistral"),
         )

# --- Main Agent Logic ---
@app.get("/enviarPregunta/{pregunta}")
async def http_mcp_questions(pregunta: str) -> None:
    try:
        logger.info(f"Recibiendo pregunta: {pregunta}")
        
        async with MCPStreamableHTTPTool(name="Servidor MCP de soporte de FACEL", url=MCP_SERVER_URL, headers={"Authorization": f"Bearer {access_token}"}) as mcp_server:
            logger.info(f"MCP agregado con exito")
            async with ChatAgent(
                chat_client=client,
                name="Support FACEL Agent",
                instructions=f"You help users with questions and errors in the 'Smartfit emision', 'Carga masiva de facturas desde OFC (Oracle Financials Cloud) con la herramienta BICC (Business Intelligence Cloud Connector)' and 'Portal de refacturacion electronica' projects. Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
            ) as agent:
                try:
                    logger.info(f"Ejecutando el agente con la pregunta: {pregunta}")
                    result = await agent.run(pregunta, tools=mcp_server)
                    logger.info(f"Resultado obtenido: {result}")
                    return result
                except asyncio.CancelledError:
                    logger.error("La tarea fue cancelada durante la ejecución del agente.")
                    return {"error": "La tarea fue cancelada durante la ejecución del agente."}
                except Exception as inner_err:
                    logger.error(f"Error durante la ejecución del agente: {str(inner_err)}")
                    return {"error": str(inner_err)}

    except anyio.WouldBlock:
        logger.warning("El flujo está bloqueado. No hay datos disponibles.")
        return {"error": "El servidor está tardando demasiado en responder."}
    except asyncio.CancelledError:
        logger.error("La solicitud fue cancelada antes de completarse.")
        return {"error": "La solicitud fue cancelada antes de completarse."}
    except Exception as err:
        logger.error(f"Error inesperado: {str(err)}")
        return {"error": str(err)}

#if __name__ == "__main__":
#    logger.info("Inicio agentframework-http-remote")