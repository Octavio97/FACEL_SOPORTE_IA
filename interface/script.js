/*function enviarPregunta() {
    try{
        fetch(`http://127.0.0.1:5000/enviarPregunta/${document.getElementById("input1").value}`)
          .then(res => res.json())
          .then(data => {
            console.log(data.message);
            console.log(data.metadata);
          });
    } catch (err) {
        alert(`Error en el envio de pregunta ${err}`);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const button = document.getElementById("btnBuscar");
    button.addEventListener("click", enviarPregunta);
});*/

function renderMetadata(metadata) {
    if (!Array.isArray(metadata) || metadata.length === 0) return null;

    const grouped = {};

    metadata.forEach(item => {
        if (!Array.isArray(item) || item.length < 2) return;

        const pageRaw = item[0]; // "page: 53"
        const fileRaw = item[1]; // "file: src/Jobs_BICC_Oracle_APEX.pdf"

        const page = pageRaw.replace('page:', '').trim();
        const filePath = fileRaw.replace('file:', '').trim();
        const fileName = filePath.split('/').pop();

        if (!grouped[fileName]) {
            grouped[fileName] = [];
        }

        grouped[fileName].push(page);
    });

    const container = document.createElement('div');
    container.classList.add('metadata');

    const title = document.createElement('div');
    title.classList.add('metadata-title');
    title.textContent = '📄 Fuentes';
    container.appendChild(title);

    Object.entries(grouped).forEach(([fileName, pages]) => {
        const uniquePages = [...new Set(pages)].sort((a, b) => a - b);

        const item = document.createElement('div');
        item.classList.add('metadata-item');
        item.textContent = `${fileName} (páginas: ${uniquePages.join(', ')})`;

        container.appendChild(item);
    });

    return container;
}

function addMessage(message, isUser, metadata = null) {
    const div = document.createElement('div');
    div.classList.add('message', isUser ? 'user' : 'bot');
    div.textContent = message;

    const messages = document.getElementById('messages');
    messages.appendChild(div);

    // 👇 Agregar metadata si viene del bot
    if (!isUser && metadata) {
        const metaBlock = renderMetadata(metadata);
        if (metaBlock) {
            messages.appendChild(metaBlock);
        }
    }

    messages.scrollTop = messages.scrollHeight;
}

function showLoader() {
    const btn = document.getElementById('sendBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="loader"></div>';
    document.getElementById('userMessage').disabled = true;
}

function hideLoader() {
    const btn = document.getElementById('sendBtn');
    btn.disabled = false;
    btn.textContent = 'Enviar';
    document.getElementById('userMessage').disabled = false;
}

function botResponse(userMessage) {
    showLoader();

    fetch(`http://127.0.0.1:5000/enviarPregunta/${encodeURIComponent(userMessage)}`)
        .then(res => res.json())
        .then(data => {
            hideLoader();
            if (data?.message) {
                addMessage(data.message, false, data.metadata);
            } else {
                addMessage("No se recibió respuesta del servidor.", false);
            }
        })
        .catch(err => {
            hideLoader();
            addMessage("Error al conectar con el servidor.", false);
            console.error(err);
        });
}

function sendMessage() {
    const input = document.getElementById('userMessage');
    const text = input.value.trim();
    if (!text) return;

    document.getElementById('welcome').hidden = document.getElementById('welcome').checkVisibility ? true : true;
    addMessage(text, true);
    input.value = '';
    botResponse(text);
}

document.getElementById('sendBtn').addEventListener('click', sendMessage);

document.getElementById('userMessage').addEventListener('keypress', e => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});
