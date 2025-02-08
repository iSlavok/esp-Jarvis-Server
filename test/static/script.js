let ws;

    function init() {
      fetch('/states')
        .then(response => response.json())
        .then(data => {
          const stateSelect = document.getElementById('stateSelect');
          data.states.forEach(s => {
            let option = document.createElement('option');
            option.value = s;
            option.text = s;
            if (s === data.current_state) option.selected = true;
            stateSelect.appendChild(option);
          });
        });

      fetch('/voices')
        .then(response => response.json())
        .then(data => {
          const voiceSelect = document.getElementById('voiceSelect');
          data.voices.forEach(voice => {
            let option = document.createElement('option');
            option.value = voice;
            option.text = voice;
            voiceSelect.appendChild(option);
          });
          loadRoles();
        });

      fetch('/client_config')
        .then(response => response.json())
        .then(data => {
          document.getElementById('audioUrl').value = data.audio_url;
          document.getElementById('volume').value = data.volume;
          document.getElementById('volumeDisplay').innerText = data.volume;
        });

      fetch('/server_config')
        .then(response => response.json())
        .then(data => {
          document.getElementById('voiceSelect').value = data.voice;
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
      console.log(JSON.stringify({ new_state: newState }));
      fetch('/update_state', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_state: newState })
      })
      .then(response => response.json())
      .then(data => {
        appendLog('clientLogs', 'State updated to ' + data.state, 'info');
      });
    }

    function updateVolume() {
        const volume = document.getElementById('volume').value;
        fetch('/update_volume', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ volume: volume })
        })
        .then(response => response.json())
        .then(data => {
          appendLog('client', 'info', 'Volume set: ' + data.volume.toString());
        });
    }

    function updateClientConfig() {
      const audioUrl = document.getElementById('audioUrl').value;
      const volume = document.getElementById('volume').value;
      fetch('/update_client_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ audio_url: audioUrl, volume: volume })
      })
      .then(response => response.json())
      .then(data => {
        appendLog('clientLogs', 'Client config updated', 'info');
      });
    }

    function updateServerConfig() {
      const voice = document.getElementById('voiceSelect').value;
      const role = document.getElementById('roleSelect').value;
      fetch('/update_server_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice: voice, role: role })
      })
      .then(response => response.json())
      .then(data => {
        appendLog('serverLogs', 'Server config updated', 'info');
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
            appendLog('server', 'info', 'State updated to ' + message.state);
        } else if (message.type === "chat") {
            appendChatMessage(message.message);
        } else {
            appendLog(message.type, message.level, message.message);
        }
      };
      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
    }

    function sendChatMessage() {
      const input = document.getElementById('chatInput');
      const messageText = input.value;
      if(messageText.trim() !== ""){
        const message = { type: "chat_message", message: messageText};
        ws.send(JSON.stringify(message));
        input.value = '';
      }
    }

    function appendLog(type, level, message) {
        console.log(message);
      const consoleDiv = document.getElementById(type);
      const currentTime = new Date().toLocaleTimeString('en-US', {hour12: false});
      const logEntry = document.createElement('div');
      logEntry.textContent = `[${currentTime}] [${level}] ${message}`;
      consoleDiv.appendChild(logEntry);
      consoleDiv.scrollTop = consoleDiv.scrollHeight;
    }

    function appendChatMessage(message) {
      const consoleDiv = document.getElementById(type);
      const currentTime = new Date().toLocaleTimeString('en-US', {hour12: false});
      const logEntry = document.createElement('div');
      logEntry.textContent = `[${currentTime}] ${message}`;
      consoleDiv.appendChild(logEntry);
      consoleDiv.scrollTop = consoleDiv.scrollHeight;
    }

    window.onload = init;