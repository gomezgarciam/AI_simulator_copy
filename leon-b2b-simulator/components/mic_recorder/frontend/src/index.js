import { Streamlit } from "streamlit-component-lib"

const recordBtn = document.getElementById("record-btn");
const statusDiv = document.getElementById("status");

let audioContext;
let processor;
let input;
let stream;
let socket;
let isRecording = false;
let metadata = {}; // Store metadata from Streamlit

function onRender(event) {
  // Capture metadata passed from Streamlit
  metadata = event.detail.args.metadata || {};
  Streamlit.setFrameHeight();
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);

// Wait a tiny bit to ensure Streamlit is ready
setTimeout(() => {
  Streamlit.setComponentReady();
}, 100);

async function startRecording() {
  isRecording = true;

  recordBtn.innerText = "Stop Recording";
  recordBtn.classList.add("recording");
  statusDiv.innerText = "Connecting...";

  try {
    // 1. Determine WebSocket URL (Universal for Nginx proxy and Cloud Shell)
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    let host = window.location.host;

    // Detect if we are in Cloud Shell Web Preview and point to port 8000
    if (host.includes("cloudshell.dev") && host.includes("8080")) {
      host = host.replace("8080", "8000");
    }

    const wsUrl = `${protocol}//${host}/ws/live-transcribe`;

    console.log("Connecting to WebSocket:", wsUrl);
    socket = new WebSocket(wsUrl);

    socket.onopen = async () => {
      console.log("WebSocket connected.");
      statusDiv.innerText = "Listening...";

      // Send dynamic metadata to backend
      socket.send(JSON.stringify({
        language: metadata.language || "English",
        sample_rate: 16000,
        target_company: metadata.target_company,
        role: metadata.role
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

      switch (data.type) {
        case "user_transcript":
          statusDiv.innerText = data.transcript;
          if (data.is_final) {
            console.log("Final Transcript:", data.transcript);
            // We can send intermediate values, but let's stick to final ones for now
            // Streamlit.setComponentValue({ type: "user_transcript", transcript: data.transcript });
          }
          break;
        case "alex_response":
          // The parent Streamlit app will play the audio.
          // We just show the transcript.
          statusDiv.innerText = `Alex: ${data.transcript}`;
          // Mute mic here if needed, or let Streamlit handle it
          break;
        case "session_report":
          console.log("Session report received:", data.report);
          statusDiv.innerText = "Session complete. See report below.";
          // Send the entire report back to Streamlit
          Streamlit.setComponentValue({ type: "session_report", report: data.report });
          stopRecording(); // End the session on the client-side
          break;
        case "error":
          console.error("Backend Error:", data.message);
          statusDiv.innerText = `Error: ${data.message}`;
          stopRecording();
          break;
        case "vad_timer_reset":
            // This is just for debugging/info, no UI change needed
            // console.log("VAD timer reset.");
            break;
        default:
          if (data.transcript) {
            statusDiv.innerText = data.transcript;
          }
          break;
      }
    };

    socket.onclose = (event) => {
      console.log("WebSocket closed with code:", event.code, "reason:", event.reason);
      // Only call stopRecording if it wasn't a clean closure initiated by the report
      if (event.code !== 1000) {
        stopRecording();
      }
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
  if (!isRecording && !socket) {
      console.log("Stop recording called but already stopped.");
      return; // Already stopped
  }

  console.log("Stopping audio capture...");
  isRecording = false;

  if (recordBtn) {
    recordBtn.innerText = "Start Recording";
    recordBtn.classList.remove("recording");
  }

  if (statusDiv && statusDiv.innerText === "Listening...") {
    statusDiv.innerText = "Ready";
  }

  // Use a try-catch for each disconnect to prevent one failure from stopping the others.
  if (processor) {
    try {
      processor.disconnect();
    } catch (e) {
      console.warn("Error disconnecting processor:", e);
    }
    processor = null;
  }
  if (input) {
    try {
      input.disconnect();
    } catch (e) {
      console.warn("Error disconnecting input:", e);
    }
    input = null;
  }
  if (audioContext && audioContext.state !== 'closed') {
    try {
        audioContext.close();
    } catch(e) {
        console.warn("Error closing audio context:", e);
    }
    audioContext = null;
  }
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  if (socket) {
    // Check readyState before closing
    if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close(1000, "Client initiated disconnect");
    }
    socket = null;
  }
  console.log("Cleanup complete.");
}

recordBtn.onclick = () => {
  if (isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
};

