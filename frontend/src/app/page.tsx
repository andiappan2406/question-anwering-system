"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { ChatInterface } from "@/components/ChatInterface";
import { RoutingTracePanel } from "@/components/RoutingTracePanel";
import { Message, RoutingTrace, UserRole, AskResponseBody } from "@/types/chat";
import { formatTimestamp } from "@/lib/utils";
import { HeroSection } from "@/components/HeroSection";
import { BACKEND_CONFIG } from "@/lib/config";
import { inferRoutingTrace } from "@/lib/traceInference";
import { DEFAULT_STUDENT_ID, DEFAULT_STAFF_ID, SAMPLE_STUDENT_IDS } from "@/lib/constants";
import { PlacementMatcherModal } from "@/components/PlacementMatcherModal";

export default function Home() {
  const [currentRole, setCurrentRole] = useState<UserRole>("student");
  const [showLanding, setShowLanding] = useState<boolean>(true);
  const [selectedStudentId, setSelectedStudentId] = useState<string>(DEFAULT_STUDENT_ID);
  const [userId, setUserId] = useState<string>(DEFAULT_STUDENT_ID);
  const [isTraceOpen, setIsTraceOpen] = useState<boolean>(false);
  const [selectedTrace, setSelectedTrace] = useState<RoutingTrace | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [useLlm, setUseLlm] = useState<boolean>(true);
  const [isPlacementModalOpen, setIsPlacementModalOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome-msg",
      role: "assistant",
      content:
        "Welcome to the Institutional Q&A System. You can inquire about student attendance, grades, GPA, fees, faculty designations, courses taught, and academic regulations. Queries are routed dynamically across L1 Cache, relational SQL databases, vector policy embeddings, and neural synthesizers.",
      timestamp: "",
      confidence: 0.98,
      sources: [
        {
          record_id: "doc_system_architecture",
          title: "Amypo Multi-Route Institutional Intelligence",
          snippet:
            "Automated dual-route reasoning engine linking relational student/faculty records with academic policy guidelines and L1 semantic cache.",
          score: 0.99,
          collection: "system_handbook",
        },
      ],
      trace: {
        path: "cache",
        latencyMs: 7,
        decisionReason: "System startup greeting loaded from memory cache.",
        cachedAt: "2026-10-02T14:30:00Z",
        cacheKey: "system:welcome:institutional",
        steps: [
          { name: "Session Initialized", status: "completed", latencyMs: 2, details: "Verified authentication & persona" },
          { name: "L1 Cache Retrieval", status: "completed", latencyMs: 5, details: "Loaded welcome parameters" },
        ],
      },
    },
  ]);

  // Set initial timestamp client-side to prevent hydration mismatch
  useEffect(() => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === "welcome-msg" && !msg.timestamp
          ? { ...msg, timestamp: formatTimestamp() }
          : msg
      )
    );
    if (messages[0]?.trace) {
      setSelectedTrace(messages[0].trace);
    }
  }, []);

  // Update userId when role changes
  const handleRoleChange = (role: UserRole) => {
    setCurrentRole(role);
    setUserId(role === "student" ? selectedStudentId : DEFAULT_STAFF_ID);
  };

  const handleStudentIdChange = (newId: string) => {
    setSelectedStudentId(newId);
    if (currentRole === "student") {
      setUserId(newId);
    }
  };

  const handleLandingRoleSelect = (role: UserRole, studentId?: string) => {
    if (studentId) {
      setSelectedStudentId(studentId);
      setUserId(role === "student" ? studentId : DEFAULT_STAFF_ID);
    } else {
      setUserId(role === "student" ? selectedStudentId : DEFAULT_STAFF_ID);
    }
    setCurrentRole(role);
    setShowLanding(false);
  };

  const handleLandingQuickQuery = (query: string, role: UserRole, studentId?: string) => {
    const activeStudentId = studentId || selectedStudentId;
    if (studentId) {
      setSelectedStudentId(studentId);
    }
    const resolvedUserId = role === "student" ? activeStudentId : DEFAULT_STAFF_ID;
    setUserId(resolvedUserId);
    setCurrentRole(role);
    setShowLanding(false);
    handleSendMessage(query, resolvedUserId, role);
  };

  const handleSendMessage = async (
    questionText: string,
    overrideUserId?: string,
    overrideRole?: UserRole
  ) => {
    const activeUserId = overrideUserId || userId;
    const activeRole = overrideRole || currentRole;
    const timestamp = formatTimestamp();

    // Append user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: questionText,
      timestamp,
      userId: activeUserId,
      userRole: activeRole,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    const startTime = Date.now();
    let data: AskResponseBody | null = null;
    let latencyMs = 0;
    let usedEndpoint = BACKEND_CONFIG.apiUrl;

    // 1. Try real FastAPI backend directly first (port 9000)
    try {
      const response = await fetch(BACKEND_CONFIG.apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: questionText,
          user_id: activeUserId,
          use_llm: useLlm,
        }),
        signal: AbortSignal.timeout(15000),
      });

      if (response.ok) {
        data = await response.json();
        latencyMs = Date.now() - startTime;
      }
    } catch {
      // Backend not running or timeout; fallback to internal Next.js API
    }

    // 2. Resilient fallback to Next.js API route (/api/v1/ask)
    if (!data && BACKEND_CONFIG.apiUrl !== "/api/v1/ask") {
      try {
        usedEndpoint = "/api/v1/ask";
        const fallbackRes = await fetch("/api/v1/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: questionText,
            user_id: activeUserId,
            use_llm: useLlm,
          }),
        });

        if (fallbackRes.ok) {
          data = await fallbackRes.json();
          latencyMs = Date.now() - startTime;
        }
      } catch (err: unknown) {
        console.error("Internal fallback route failed:", err);
      }
    }

    if (data) {
      const trace = inferRoutingTrace(data, latencyMs, usedEndpoint);

      const assistantMsg: Message = {
        id: `asst-${Date.now()}`,
        role: "assistant",
        content: data.answer,
        timestamp: formatTimestamp(),
        confidence: data.confidence,
        sources: data.sources,
        trace: trace,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setSelectedTrace(trace);
    } else {
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: `Could not reach the QA service. Please ensure the backend is running at ${BACKEND_CONFIG.apiUrl} or check network connectivity.`,
        timestamp: formatTimestamp(),
        confidence: 0.15,
        sources: [],
      };
      setMessages((prev) => [...prev, errorMsg]);
    }

    setIsLoading(false);
  };

  const handleSelectTrace = (msg: Message) => {
    if (msg.trace) {
      setSelectedTrace(msg.trace);
      setIsTraceOpen(true);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setSelectedTrace(null);
  };

  return (
    <div
      className={`flex flex-col w-screen bg-[#FAF8F5] text-stone-900 font-sans select-text ${
        showLanding ? "h-auto min-h-screen overflow-y-auto" : "h-screen overflow-hidden"
      }`}
    >
      {showLanding ? (
        <HeroSection
          onSelectRole={handleLandingRoleSelect}
          onRunQuickQuery={handleLandingQuickQuery}
          studentId={selectedStudentId}
          onStudentIdChange={handleStudentIdChange}
        />
      ) : (
        <>
          {/* Top Navigation Bar */}
          <Header
            currentRole={currentRole}
            onRoleChange={handleRoleChange}
            userId={userId}
            onStudentIdChange={handleStudentIdChange}
            availableStudentIds={SAMPLE_STUDENT_IDS}
            lastRoutingPath={selectedTrace?.path || null}
            lastLatencyMs={selectedTrace?.latencyMs || null}
            isTraceOpen={isTraceOpen}
            onToggleTrace={() => setIsTraceOpen(!isTraceOpen)}
            onClearChat={handleClearChat}
            messageCount={messages.length}
            useLlm={useLlm}
            onToggleLlm={() => setUseLlm((prev) => !prev)}
            onOpenPlacementMatcher={() => setIsPlacementModalOpen(true)}
          />

          {/* Main Container: Chat on Left, Collapsible Routing Trace Panel on Right */}
          <div className="flex-1 flex min-h-0 relative overflow-hidden">
            {/* Chat Interface */}
            <ChatInterface
              messages={messages}
              isLoading={isLoading}
              onSendMessage={(q) => handleSendMessage(q)}
              currentRole={currentRole}
              userId={userId}
              onSelectTrace={handleSelectTrace}
              useLlm={useLlm}
              onToggleLlm={() => setUseLlm((prev) => !prev)}
            />

            {/* Collapsible Routing Trace Side Panel */}
            <RoutingTracePanel
              trace={selectedTrace}
              isOpen={isTraceOpen}
              onToggle={() => setIsTraceOpen(!isTraceOpen)}
              useLlm={useLlm}
              onToggleLlm={() => setUseLlm((prev) => !prev)}
            />
          </div>
        </>
      )}

      {/* Interactive Placement & Skill Matcher Modal */}
      <PlacementMatcherModal
        isOpen={isPlacementModalOpen}
        onClose={() => setIsPlacementModalOpen(false)}
        activeStudentId={selectedStudentId}
        onStudentIdChange={handleStudentIdChange}
        onSelectQuery={(q) => {
          setShowLanding(false);
          handleSendMessage(q);
        }}
      />
    </div>
  );
}