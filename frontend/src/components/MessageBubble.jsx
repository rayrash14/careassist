// ✅ MessageBubble.jsx
import { useState, useRef, useEffect } from "react";

export default function MessageBubble({
  role,
  type = "text",
  content,
  title,
  items,
  url,
  lang = "en",
  summary,
  source,
  audioUrl
}) {
  const align = role === "user" ? "justify-end" : "justify-start";
  const bg = role === "user" ? "bg-indigo-100" : "bg-white";
  const isAssistant = role === "assistant";

  const [isPlaying, setIsPlaying] = useState(false);
  const [ttsAudioUrl, setTtsAudioUrl] = useState(null);
  const audioRef = useRef(null);

  const isUserWithAudio = role === "user" && audioUrl;

  useEffect(() => {
    if (isUserWithAudio) {
      audioRef.current = new Audio(audioUrl);
    }
  }, [audioUrl, isUserWithAudio]);

  const fetchTTS = async () => {
    const res = await fetch("http://localhost:8000/api/voice/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: content, lang })
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    setTtsAudioUrl(url);
    audioRef.current = new Audio(url);
  };

  const togglePlayback = async () => {
    if (!audioRef.current) {
      await fetchTTS();
    }

    if (audioRef.current.paused) {
      audioRef.current.play();
      setIsPlaying(true);
      audioRef.current.onended = () => setIsPlaying(false);
    } else {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  return (
    <div className={`flex ${align}`}>
      <div className={`max-w-xs p-3 text-sm rounded shadow ${bg} relative`}>
        {type === "text" && (
          <>
            {content}
            {isAssistant && (
              <button
                onClick={togglePlayback}
                className={`mt-2 w-full py-1 border rounded text-sm font-medium ${
                  isPlaying ? "bg-gray-200 text-gray-700" : "bg-gray-100 hover:bg-indigo-100 text-indigo-600"
                }`}
              >
                {isPlaying ? "Pause 🔊" : "Play 🔊"}
              </button>
            )}
          </>
        )}

        {isUserWithAudio && (
          <button
            onClick={togglePlayback}
            className={`mt-2 w-full py-1 border rounded text-sm font-medium ${
              isPlaying ? "bg-gray-200 text-gray-700" : "bg-gray-100 hover:bg-indigo-100 text-indigo-600"
            }`}
          >
            {isPlaying ? "Pause 🔊" : "Play 🔊"}
          </button>
        )}

        {type === "checklist" && (
          <div>
            <div className="font-semibold mb-2">{title}</div>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {items.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {type === "video" && (
          <div>
            <div className="font-semibold mb-2">{title}</div>
            <div className="aspect-video mb-2">
              <iframe
                className="w-full h-full rounded"
                src={url}
                title="CareAssist Video"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
            {summary && <p className="text-gray-700 text-sm mb-1">{summary}</p>}
          </div>
        )}

        {source && (
          <div className="text-xs text-gray-400 mt-2">
            Source: {source}
          </div>
        )}
      </div>
    </div>
  );
}
