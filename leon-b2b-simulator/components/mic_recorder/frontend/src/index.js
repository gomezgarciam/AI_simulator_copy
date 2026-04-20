import { Streamlit } from "streamlit-component-lib"

const recordBtn = document.getElementById("record-btn");
const statusDiv = document.getElementById("status");

let audioContext;
let processor;
let input;
let stream;
let socket;
let isRecording = false;

function onRender(event) {
  Streamlit.setFrameHeight();
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();

async function startRecording() {
  isRecording = true;
  recordBtn.innerText = "Stop Recording";
  recordBtn.classList.add("recording");
  statusDiv.innerText = "Connecting...";

  try {
    // 1. Determine WebSocket URL
    let wsUrl = "ws://localhost:8000/ws/live-transcribe";
    
    if (window.location.hostname.includes("devshell.dev") || window.location.hostname.includes("appspot.com")) {
      const parts = window.location.hostname.split("-dot-");
      if (parts.length > 1) {
        const shellId = parts.slice(1).join("-dot-");
        wsUrl = `wss://8000-dot-${shellId}/ws/live-transcribe`;
      }
    }

    console.log("Connecting to WebSocket:", wsUrl);
    socket = new WebSocket(wsUrl);

    socket.onopen = async () => {
      console.log("WebSocket connected.");
      statusDiv.innerText = "Listening...";
      
      socket.send(JSON.stringify({
        language: "English",
        sample_rate: 16000
      }));

      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      input = audioContext.createMediaStreamSource(stream);
      
      processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      processor.onaudioprocess = (e) => {
        if (!isRecording) return;
        
        const inputData = e.inputBuffer.getChannelData(0);
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(pcmData.buffer);
        }
      };

      input.connect(processor);
      processor.connect(audioContext.destination);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      statusDiv.innerText = data.transcript;
      if (data.is_final) {
        console.log("Final Transcript:", data.transcript);
        Streamlit.setComponentValue(data.transcript);
      }
    };

    socket.onclose = () => {
      console.log("WebSocket closed.");
      stopRecording();
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      statusDiv.innerText = "Error!";
      stopRecording();
    };

  } catch (err) {
    console.error("Error starting recording:", err);
    statusDiv.innerText = "Permission Denied!";
    stopRecording();
  }
}

function stopRecording() {
  isRecording = false;
  recordBtn.innerText = "Start Recording";
  recordBtn.classList.remove("recording");
  
  if (statusDiv.innerText === "Listening...") {
    statusDiv.innerText = "Ready";
  }

  if (processor) {
    processor.disconnect();
    processor = null;
  }
  if (input) {
    input.disconnect();
    input = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  if (socket) {
    socket.close();
    socket = null;
  }
}

recordBtn.onclick = () => {
  if (isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
};
