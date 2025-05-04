// ✅ Chat.jsx — Welcome message adapted by language
import { useState, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import useAudioRecorder from "../hooks/useAudioRecorder";

const getWelcomeMessage = (lang) =>
  lang === "hi"
    ? "नमस्कार! मैं केयरअसिस्ट हूं। आज मैं आपकी कैसे मदद कर सकता हूं?"
    : "Hi! I'm CareAssist. How can I support you today?";

export default function Chat() {
  const [lang, setLang] = useState("en");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        type: "text",
        content: getWelcomeMessage(lang),
      },
    ]);
  }, [lang]);

  const handleTranscription = async (transcript, audioBlob, audioUrl) => {
    const userCombinedMsg = {
      role: "user",
      type: "text",
      content: transcript,
      audioUrl,
    };
    setMessages((prev) => [...prev, userCombinedMsg]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: transcript, lang }),
      });

      const chatText = await res.text();
      const chatData = JSON.parse(chatText);

      const structuredMsg =
        chatData.type === "checklist" || chatData.type === "video"
          ? { role: "assistant", ...chatData }
          : {
              role: "assistant",
              type: "text",
              content: chatData.content || chatData.answer,
            };

      setMessages((prev) => [...prev, structuredMsg]);
    } catch (err) {
      console.error("Voice reply error:", err);
    }

    setLoading(false);
  };

  const { startRecording, stopRecording, recording: isRecording } = useAudioRecorder(
    (...args) => handleTranscription(...args, lang)
  );

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", type: "text", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input, lang }),
      });

      const text = await res.text();
      const data = JSON.parse(text);

      const structuredMsg =
        data.type === "checklist" || data.type === "video"
          ? { role: "assistant", ...data }
          : {
              role: "assistant",
              type: "text",
              content: data.content || data.answer,
            };

      setMessages((prev) => [...prev, structuredMsg]);
    } catch (err) {
      console.error("API error:", err);
    }

    setLoading(false);
  };

  const handleMicClick = () => {
    isRecording ? stopRecording() : startRecording();
  };

  return (
    <div className="flex flex-col flex-1">
      <div className="flex items-center justify-end px-4 py-2">
        <label className="mr-2 text-sm">🌐 Language:</label>
        <select
          value={lang}
          onChange={(e) => setLang(e.target.value)}
          className="text-sm border rounded px-2 py-1"
        >
          <option value="en">English</option>
          <option value="hi">Hindi</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <MessageBubble key={i} {...msg} lang={lang} />
        ))}
        {loading && (
          <div className="text-sm text-gray-500 italic">
            CareAssist is typing...
          </div>
        )}
      </div>

      <div className="border-t p-3 bg-white flex gap-2">
        <input
          className="flex-1 border rounded px-3 py-2 text-sm"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          className="bg-indigo-600 text-white px-4 rounded"
          onClick={sendMessage}
          disabled={loading}
        >
          Send
        </button>
        <button
          className={`bg-green-500 text-white px-4 rounded ${
            isRecording ? "animate-pulse" : ""
          }`}
          onClick={handleMicClick}
        >
          {isRecording ? "Stop 🎙️" : "Mic 🎤"}
        </button>
      </div>
    </div>
  );
}
