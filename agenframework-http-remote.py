import logging
import os
from datetime import datetime
from rich.logging import RichHandler
from agent_framework.openai import OpenAIChatClient
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from flask import Flask
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("agentframework-http-remote")
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://facel-soporte-ia.fastmcp.app/mcp")
API_HOST = os.getenv("API_HOST", "ollama")

client = OpenAIChatClient(
        base_url=os.environ.get("OLLAMA_ENDPOINT", "http://127.0.0.1:11434/"),
        api_key="none",
        model_id=os.environ.get("OLLAMA_MODEL", "deepseek-r1:8b"),
    )

# --- Main Agent Logic ---
@app.route("/enviarPregunta/<path:pregunta>", methods=['GET'])
async def http_mcp_example(pregunta) -> str:
    async with (
        MCPStreamableHTTPTool(name="Servidor MCP de soporte de FACEL", url=MCP_SERVER_URL) as mcp_server,
        ChatAgent(
            chat_client=client,
            name="Support FACEL Agent",
            instructions=f"You help users with questions and errors in the 'Smartfit emision', 'Carga masiva de facturas desde OFC (Oracle Financials Cloud) con la herramienta BICC (Business Intelligence Cloud Connector)' and 'Portal de refacturacion electronica' projects. Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
        ) as agent,
    ):
        try:
            if pregunta.lower() == 'salir':
                return {"message": "salir de la app"}

            result = await agent.run(pregunta, tools=mcp_server)
            
            print(result)
        except Exception as err:
            print(str(err))
        finally:
            print(result)

if __name__ == "__main__":
    http_mcp_example()