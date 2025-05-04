// hooks/useAudioRecorder.js
import { useState, useRef } from "react";

export default function useAudioRecorder(onTranscription) {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audioFile = new File([audioBlob], "recording.wav", { type: "audio/wav" });

        const formData = new FormData();
        formData.append("file", audioFile);
        formData.append("lang", "en");

        try {
          const res = await fetch("http://localhost:8000/api/voice/transcribe", {
            method: "POST",
            body: formData
          });

          if (res.ok) {
            const data = await res.json();
            onTranscription(data.transcript, audioBlob, audioUrl);
          }
        } catch (err) {
          console.error("Transcription failed:", err);
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Microphone error:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return { recording, startRecording, stopRecording };
}
