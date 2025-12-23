import logging
import os
from datetime import datetime
from rich.logging import RichHandler
from agent_framework.openai import OpenAIChatClient
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import anyio

origins = [
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
]


# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("agentframework-http-remote")
logger.setLevel(logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://facel-soporte-ia.fastmcp.app/mcp")
API_HOST = os.getenv("API_HOST", "ollama")
access_token = os.getenv("ACCESS_TOKEN","fmcp_xpmxheUukEZfauKWNHUY0RvFN5fZh8GICBicJOXb6i0")

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
                instructions=f"You help users with questions and errors in the 'Smartfit emision', 'Carga masiva de facturas desde OFC (Oracle Financials Cloud) con la herramienta BICC (Business Intelligence Cloud Connector)' and 'Portal de refacturacion electronica' projects. Answer in the same language as the question. Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
            ) as agent:
                try:
                    logger.info(f"Ejecutando el agente con la pregunta: {pregunta}")
                    result = await agent.run(pregunta, tools=mcp_server)
                    logger.info(f"Resultado obtenido: {result}")
                    return { "status": "1", "message":  str(result.messages[0].contents[0].text)}
                    #return result
                except asyncio.CancelledError:
                    logger.error("La tarea fue cancelada durante la ejecución del agente.")
                    return {"status": "0", "message": "La tarea fue cancelada durante la ejecución del agente."}
                except Exception as inner_err:
                    logger.error(f"Error durante la ejecución del agente: {str(inner_err)}")
                    return {"status": "0", "message": str(inner_err)}

    except anyio.WouldBlock:
        logger.warning("El flujo está bloqueado. No hay datos disponibles.")
        return {"status": "0", "message": "El servidor está tardando demasiado en responder."}
    except asyncio.CancelledError:
        logger.error("La solicitud fue cancelada antes de completarse.")
        return {"status": "0", "message": "La solicitud fue cancelada antes de completarse."}
    except Exception as err:
        logger.error(f"Error inesperado: {str(err)}")
        return {"status": "0", "message": str(err)}

#if __name__ == "__main__":
#    logger.info("Inicio agentframework-http-remote")