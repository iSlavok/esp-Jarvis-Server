let ws;

function init() {
    fetch('/config')
        .then(response => response.json())
        .then(data => {
            const stateSelect = document.getElementById('stateSelect');
            data.states.forEach(s => {
                let option = document.createElement('option');
                option.value = s;
                option.text = s;
                stateSelect.appendChild(option);
            });
            stateSelect.value = data.current_state
            document.getElementById('audioUrl').value = data.audio_url;
            document.getElementById('volume').value = data.volume;
            document.getElementById('volumeDisplay').innerText = data.volume;
            const voiceSelect = document.getElementById('voiceSelect');
            data.voices.forEach(voice => {
                let option = document.createElement('option');
                option.value = voice;
                option.text = voice;
                voiceSelect.appendChild(option);
            });
            voiceSelect.value = data.voice;
            loadRoles(() => {
                document.getElementById('roleSelect').value = data.role;
            });
        });

    document.getElementById('volume').addEventListener('input', function() {
        document.getElementById('volumeDisplay').innerText = this.value;
    });

    initWebSocket();
}

function loadRoles(callback) {
    const voice = document.getElementById('voiceSelect').value;
    fetch('/roles?voice=' + voice)
        .then(response => response.json())
        .then(data => {
            const roleSelect = document.getElementById('roleSelect');
            roleSelect.innerHTML = '';
            data.roles.forEach(role => {
                let option = document.createElement('option');
                option.value = role;
                option.text = role;
                roleSelect.appendChild(option);
            });
            if(callback) callback();
        });
}

function changeState() {
    const newState = document.getElementById('stateSelect').value;
    fetch('/update_state', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({new_state: newState})
    })
}

function updateHost() {
    const audioUrl = document.getElementById('audioUrl').value;
    fetch('/update_host', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ host: audioUrl })
    })
}

function updateVolume() {
    const volume = document.getElementById('volume').value;
    fetch('/update_volume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ volume: volume })
    })
}

function updateVoice() {
    const voice = document.getElementById('voiceSelect').value;
    const role = document.getElementById('roleSelect').value;
    fetch('/update_voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice: voice, role: role})
    })
}

function clearChat() {
    fetch('/clear_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => {
        document.getElementById('chatConsole').innerHTML = '';
    });
}

function initWebSocket() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.onopen = () => {
        console.log('WebSocket connected');
    };
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === "state") {
            document.getElementById('stateSelect').value = message.state;
            appendLog('server', 'State updated to ' + message.state);
        } else if (message.type === "chat") {
            appendChatMessage(message.message, false);
        } else {
            appendLog(message.type, message.message);
        }
    };
    ws.onclose = () => {
        console.log('WebSocket disconnected');
    };
}

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const messageText = input.value;
    if (messageText.trim() !== "") {
        const message = { type: "chat_message", message: messageText};
        ws.send(JSON.stringify(message));
        appendChatMessage(messageText, true);
        input.value = '';
    }
}

function appendLog(type, message) {
    const consoleDiv = document.getElementById(type);
    const currentTime = new Date().toLocaleTimeString('en-US', {hour12: false});
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${currentTime}] ${message}`;
    consoleDiv.appendChild(logEntry);
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

function appendChatMessage(message, isSent) {
    const consoleDiv = document.getElementById("chatConsole");
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("chat-message");
    messageDiv.classList.add(isSent ? "sent" : "received");

    messageDiv.style.alignSelf = isSent ? "flex-end" : "flex-start";

    const currentTime = new Date().toLocaleTimeString('en-US', { hour12: false });
    messageDiv.textContent = isSent ? `${message} [${currentTime}]` : `[${currentTime}] ${message}`;

    consoleDiv.appendChild(messageDiv);
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}


window.onload = init;