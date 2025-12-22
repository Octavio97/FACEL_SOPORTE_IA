from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from cargarDatos import cargar_documentos, crear_vectorstore
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

api_info = {
    "status": "ACTIVO",
    "version": "v1.0.0",
    "last_check": "2025-12-15 21:27:00",
    "endpoints": [
        {"method": "GET", "path": "/inicializarServicio", "desc": "Inicializar modelo de IA"},
        {"method": "POST", "path": "/enviarPregunta", "desc": "Responder pregunta sobre proyecto"}
    ]
}

endpoints_html = "".join([
    f'''
    <div class="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg border border-slate-700 mb-2">
        <div class="flex items-center space-x-3">
            <span class="text-xs font-bold px-2 py-1 rounded bg-blue-500/20 text-blue-400 w-16 text-center">{e['method']}</span>
            <code class="text-sm text-slate-300">{e['path']}</code>
        </div>
        <span class="text-xs text-slate-500 italic">{e['desc']}</span>
    </div>
    ''' for e in api_info["endpoints"]
])

api_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Gateway | Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }}
        .glow {{ box-shadow: 0 0 20px rgba(34, 197, 94, 0.1); }}
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="max-w-2xl w-full p-8 bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 glow">
        
        <!-- Encabezado con Status Dinámico -->
        <div class="flex items-center justify-between mb-8">
            <div>
                <h1 class="text-2xl font-bold text-white">API Gateway</h1>
                <p class="text-xs text-slate-500 mt-1">Última comprobación: {api_info['last_check']}</p>
            </div>
            <span class="px-4 py-1 text-xs font-bold text-green-400 bg-green-400/10 border border-green-400/20 rounded-full animate-pulse">
                {api_info['status']}
            </span>
        </div>

        <!-- Lista de Endpoints -->
        <div class="mb-8">
            <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Endpoints Disponibles</h2>
            <div class="max-h-64 overflow-y-auto pr-2 custom-scrollbar">
                {endpoints_html}
            </div>
        </div>

        <!-- Botones de Acción -->
        <div class="grid grid-cols-2 gap-4 border-t border-slate-700 pt-6">
            <a href="/docs" class="flex items-center justify-center p-3 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 transition-all hover:scale-[1.02]">
                📄 Ver Documentación
            </a>
            <a href="/health" class="flex items-center justify-center p-3 text-sm font-medium text-slate-300 bg-slate-700 rounded-lg hover:bg-slate-600 transition-all">
                🔍 Check de Salud
            </a>
        </div>

        <footer class="mt-8 text-center">
            <p class="text-[10px] text-slate-600 uppercase tracking-widest">
                © 2025 API Service {api_info['version']} • Running on Python
            </p>
        </footer>
    </div>
</body>
</html>
"""

def inicializarServicio():
    try:
        global qa
        ruta_archivo = "src/Jobs_BICC_Oracle_APEX.pdf"#"src/HAI_2024_AI-Index-Report.pdf"
        llm = Ollama(model="deepseek-r1:8b")
        embed_model = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        vectorstore = Chroma(embedding_function=embed_model,
                                           persist_directory="chroma_db_dir",
                                           collection_name="stanford_report_data")
        total_rows = len(vectorstore.get()['ids'])
        if total_rows == 0:
            docs = cargar_documentos(ruta_archivo)
            vectorstore = crear_vectorstore(docs)
        retriever = vectorstore.as_retriever(search_kwargs={'k': 4})

        custom_prompt_template = """Use the following pieces of information to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context: {context}
        Question: {question}

        Only return the helpful answer below and nothing else but in spanish.
        Helpful answer:
        """
        prompt = PromptTemplate(template=custom_prompt_template, input_variables=['context', 'question'])

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        return {"message": "Servicio inicializado correctamente"}
    except Exception as err:
        qa = {"message": str(err)}
    finally:
        return qa