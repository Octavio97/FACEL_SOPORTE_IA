from fastmcp import FastMCP
import logging
import os
import fitz
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("facel_chat_ia_mcp_http_remote")

SCRIPT_DIR = Path(__file__).parent
SOURCE_DIRECTORY = SCRIPT_DIR / "src"

app = FastMCP("SOPORTE_FACEL_IA")

def leer_pdf(ruta_pdf):
    documento = fitz.open(ruta_pdf)
    texto = ""
    
    for pagina in documento:
        texto += pagina.get_text()
    
    return texto

@app.tool
def answer_question(text: str) -> str:
    """Return data with any prompt"""
    return {"message" : f"{text}"}

@app.resource("resource://src")
async def read_documentation():
    """  
    Function to process all PDF files in a folder and store them as FastMCP resources.

    Parameters:

    SOURCE_DIRECTORY (str): Path to the folder containing the PDF files.
    """
    logger.info("Accediste a datos de la documentacion del proyecto")
    archivos_pdf = [f for f in os.listdir(SOURCE_DIRECTORY) if f.endswith('.pdf')]
    
    contenido_archivos = {}
    
    for archivo in archivos_pdf:
        ruta_pdf = os.path.join(SOURCE_DIRECTORY, archivo)
        contenido = leer_pdf(ruta_pdf)
        contenido_archivos[archivo] = contenido
    
    return contenido_archivos

@app.prompt
def analize_question_prompt():
    return f"""
    Use the following documents in the directory {SOURCE_DIRECTORY} to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Only return the helpful answer below and nothing else but in spanish.
    Helpful answer:
    """
#RUN LOCAL MCP
#if __name__ == "__main__":  
#    logger.info("Servidor MCP inicializando")
#    #inicializarServicio()
#    #app.run()
#    app.run(transport="streamable-http", host="0.0.0.0", port=3000)