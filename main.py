from fastmcp import FastMCP
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_community.llms import Ollama
from inicializarServico import inicializarServicio
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("ExpensesMCP")

SCRIPT_DIR = Path(__file__).parent
SOURCE_DIRECTORY = SCRIPT_DIR / "src"

app = FastMCP("SOPORTE_FACEL_IA")

@app.tool
def test_data(text: str) -> str:
    """Return data with any prompt"""
    return {"message" : f"{text}"}

if __name__ == "__main__":  
    logger.info("Servidor MCP inicializando")
    #inicializarServicio()
    #app.run()
    app.run(transport="streamable-http", host="0.0.0.0", port=3000)