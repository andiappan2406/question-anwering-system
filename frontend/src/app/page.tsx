"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Send, User, Bot, AlertTriangle, ShieldCheck } from "lucide-react";

type Source = {
  record_id: string;
  snippet: string;
};

type Message = {
  role: "user" | "system";
  content: string;
  confidence?: number;
  sources?: Source[];
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [userId, setUserId] = useState("U101");
  const [useLlm, setUseLlm] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    // Setup Speech Recognition
    if (typeof window !== "undefined") {
      const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = "en-US";

        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
          setIsRecording(false);
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error("Speech recognition error", event.error);
          setIsRecording(false);
        };

        recognitionRef.current.onend = () => {
          setIsRecording(false);
        };
      }
    }
  }, []);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
    } else {
      if (recognitionRef.current) {
        recognitionRef.current.start();
        setIsRecording(true);
      } else {
        alert("Speech recognition is not supported in this browser.");
      }
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: input,
          user_id: userId || null,
          use_llm: useLlm,
        }),
      });

      if (!res.ok) throw new Error("Failed to fetch");

      const data = await res.json();
      
      const systemMessage: Message = {
        role: "system",
        content: data.answer || "I could not find a confident answer for your question.",
        confidence: data.confidence,
        sources: data.sources,
      };

      setMessages((prev) => [...prev, systemMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [...prev, { role: "system", content: "Error connecting to the backend server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 dark:bg-zinc-900 font-sans text-slate-900 dark:text-slate-100 transition-colors">
      {/* Header Settings */}
      <header className="flex items-center justify-between px-6 py-4 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md border-b border-slate-200 dark:border-zinc-800 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/20">
            <Bot className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight">AMYPO Q&A</h1>
            <p className="text-xs text-slate-500 font-medium">Local Database Agent</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-sm bg-slate-100 dark:bg-zinc-800 px-4 py-2 rounded-full border border-slate-200 dark:border-zinc-700">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="User ID (optional)"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="bg-transparent border-none outline-none w-20 text-slate-700 dark:text-slate-300 placeholder-slate-400 font-medium"
            />
          </div>
          <div className="w-px h-4 bg-slate-300 dark:bg-zinc-700"></div>
          <label className="flex items-center gap-2 cursor-pointer group">
            <span className="text-slate-600 dark:text-slate-400 font-medium group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">Use LLM Fallback</span>
            <input 
              type="checkbox" 
              checked={useLlm}
              onChange={(e) => setUseLlm(e.target.checked)}
              className="w-4 h-4 accent-indigo-600 cursor-pointer"
            />
          </label>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 max-w-4xl w-full mx-auto">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 text-slate-500 opacity-80 mt-10">
            <div className="w-20 h-20 bg-indigo-100 dark:bg-indigo-900/30 rounded-full flex items-center justify-center mb-2 shadow-inner">
              <Bot className="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-200">How can I help you today?</h2>
            <p className="max-w-md">Ask me about AMYPO course content, FAQs, policies, or check your personal academic records.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
            <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-5 py-4 shadow-sm ${
              msg.role === "user" 
                ? "bg-gradient-to-br from-indigo-500 to-indigo-600 text-white rounded-br-none" 
                : "bg-white dark:bg-zinc-800 border border-slate-100 dark:border-zinc-700 text-slate-800 dark:text-slate-200 rounded-bl-none shadow-md shadow-slate-200/20 dark:shadow-none"
            }`}>
              <div className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</div>
              
              {msg.role === "system" && msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-100 dark:border-zinc-700/50">
                  <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                    Grounded Source
                  </div>
                  {msg.sources.map((s, i) => (
                    <div key={i} className="bg-slate-50 dark:bg-zinc-900/50 p-3 rounded-lg border border-slate-100 dark:border-zinc-700/50 text-sm">
                      <span className="inline-block px-2 py-0.5 bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 rounded text-xs font-mono font-medium mb-2">
                        {s.record_id}
                      </span>
                      <p className="text-slate-600 dark:text-slate-400 italic">"{s.snippet}"</p>
                    </div>
                  ))}
                </div>
              )}

              {msg.role === "system" && typeof msg.confidence === "number" && (
                <div className={`mt-3 flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-md w-fit ${
                  msg.confidence > 0.7 ? "bg-emerald-50 text-emerald-700 border border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800/30 dark:text-emerald-400" :
                  msg.confidence > 0.4 ? "bg-amber-50 text-amber-700 border border-amber-100 dark:bg-amber-900/20 dark:border-amber-800/30 dark:text-amber-400" :
                  "bg-rose-50 text-rose-700 border border-rose-100 dark:bg-rose-900/20 dark:border-rose-800/30 dark:text-rose-400"
                }`}>
                  <AlertTriangle className="w-3 h-3" />
                  Confidence: {(msg.confidence * 100).toFixed(1)}%
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-zinc-800 border border-slate-100 dark:border-zinc-700 rounded-2xl rounded-bl-none px-5 py-4 shadow-sm flex gap-2 items-center">
              <div className="w-2 h-2 rounded-full bg-slate-300 dark:bg-zinc-600 animate-bounce" style={{ animationDelay: "0ms" }} />
              <div className="w-2 h-2 rounded-full bg-slate-300 dark:bg-zinc-600 animate-bounce" style={{ animationDelay: "150ms" }} />
              <div className="w-2 h-2 rounded-full bg-slate-300 dark:bg-zinc-600 animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="p-4 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md border-t border-slate-200 dark:border-zinc-800">
        <div className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            className="w-full bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 text-slate-900 dark:text-slate-100 rounded-full pl-5 pr-24 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all shadow-inner"
            placeholder="Ask about policies, records, or course material..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={isLoading}
          />
          <div className="absolute right-2 flex items-center gap-1">
            <button
              onClick={toggleRecording}
              className={`p-2.5 rounded-full transition-colors flex items-center justify-center ${
                isRecording 
                  ? "bg-rose-100 text-rose-600 hover:bg-rose-200 dark:bg-rose-900/30 dark:text-rose-400" 
                  : "text-slate-400 hover:text-slate-600 hover:bg-slate-200 dark:hover:text-slate-200 dark:hover:bg-zinc-800"
              }`}
              title="Voice Input"
            >
              {isRecording ? <Mic className="w-5 h-5 animate-pulse" /> : <MicOff className="w-5 h-5" />}
            </button>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="p-2.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md shadow-indigo-600/20 flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
        <div className="text-center mt-3 text-[10px] text-slate-400 font-medium">
          AMYPO Internal System • Stage 1 Demo
        </div>
      </footer>
    </div>
  );
}
