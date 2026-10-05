"use client";

import React, { useState, useEffect, useRef } from "react";
import { Mic, MicOff, AlertCircle, Volume2 } from "lucide-react";
import { cn } from "@/lib/utils";

// Minimal interface for browser SpeechRecognition API
interface IWindowSpeechRecognition {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onstart: (() => void) | null;
  onresult: ((event: {
    resultIndex: number;
    results: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal: boolean }>;
  }) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
}

interface VoiceMicButtonProps {
  onTranscript: (transcript: string) => void;
  disabled?: boolean;
  className?: string;
}

export function VoiceMicButton({
  onTranscript,
  disabled = false,
  className,
}: VoiceMicButtonProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const recognitionRef = useRef<IWindowSpeechRecognition | null>(null);

  useEffect(() => {
    // Check Web Speech API support safely in effect
    const windowObj = typeof window !== "undefined" ? (window as unknown as Record<string, unknown>) : null;
    const SpeechRecognitionClass =
      windowObj && (windowObj.SpeechRecognition || windowObj.webkitSpeechRecognition);

    if (!SpeechRecognitionClass) {
      const timer = setTimeout(() => setIsSupported(false), 0);
      return () => clearTimeout(timer);
    }

    try {
      const RecognitionConstructor = SpeechRecognitionClass as new () => IWindowSpeechRecognition;
      const recognition = new RecognitionConstructor();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListening(true);
        setErrorMessage(null);
      };

      recognition.onresult = (event) => {
        let finalTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const item = event.results[i];
          if (item.isFinal) {
            finalTranscript += item[0].transcript;
          }
        }
        if (finalTranscript.trim()) {
          onTranscript(finalTranscript.trim());
        }
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        if (event.error === "not-allowed") {
          setErrorMessage("Microphone access denied. Please allow microphone permissions.");
        } else if (event.error === "no-speech") {
          setErrorMessage("No speech detected. Please try speaking again.");
        } else {
          setErrorMessage(`Speech error: ${event.error}`);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } catch (err) {
      console.error("Failed to initialize SpeechRecognition:", err);
      const timer = setTimeout(() => setIsSupported(false), 0);
      return () => clearTimeout(timer);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [onTranscript]);

  const toggleListening = () => {
    if (!isSupported) {
      setErrorMessage("Web Speech API is not supported in this browser. Try Chrome, Edge, or Safari.");
      return;
    }

    if (disabled) return;

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      setErrorMessage(null);
      try {
        recognitionRef.current?.start();
      } catch (err) {
        console.error("Error starting speech recognition:", err);
        recognitionRef.current?.abort();
        setTimeout(() => {
          try {
            recognitionRef.current?.start();
          } catch (e) {
            console.error("Retry failed:", e);
          }
        }, 150);
      }
    }
  };

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={toggleListening}
        disabled={disabled}
        aria-label={isListening ? "Stop voice listening" : "Start voice input"}
        title={
          !isSupported
            ? "Voice input not supported in this browser"
            : isListening
              ? "Click to stop listening"
              : "Click to speak via Web Speech API"
        }
        className={cn(
          "relative p-2.5 rounded-xl transition-all duration-150 cursor-pointer flex items-center justify-center select-none shadow-xs",
          isListening
            ? "bg-[#8C4640] text-white mic-active-pulse"
            : isSupported
              ? "bg-stone-100 hover:bg-stone-200 text-stone-600 hover:text-stone-900 border border-stone-300"
              : "bg-stone-50 text-stone-300 border border-stone-200 cursor-not-allowed",
          disabled && "opacity-50 cursor-not-allowed",
          className
        )}
      >
        {isListening ? (
          <div className="relative flex items-center justify-center">
            <Mic className="w-4 h-4 animate-bounce" />
            <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-white animate-ping" />
          </div>
        ) : isSupported ? (
          <Mic className="w-4 h-4" />
        ) : (
          <MicOff className="w-4 h-4" />
        )}
      </button>

      {/* Floating listening / error popup */}
      {(isListening || errorMessage) && (
        <div className="absolute bottom-full right-0 mb-3 z-50 p-2.5 rounded-xl bg-stone-900/95 border border-stone-700 text-xs text-stone-100 shadow-xl backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150 min-w-48 whitespace-nowrap">
          {isListening ? (
            <div className="flex items-center gap-2 text-[#D3A29B] font-medium">
              <span className="w-2 h-2 rounded-full bg-[#8C4640] animate-ping" />
              <Volume2 className="w-3.5 h-3.5" />
              <span>Listening... Speak into microphone</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-amber-500">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate max-w-xs">{errorMessage}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
