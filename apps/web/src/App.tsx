import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { JobInboxScreen } from "./components/JobInboxScreen";
import { JobDetailScreen } from "./components/JobDetailScreen";
import { ProposalStudioScreen } from "./components/ProposalStudioScreen";
import { PipelineBoardScreen } from "./components/PipelineBoardScreen";
import { MessagesScreen } from "./components/MessagesScreen";
import { AgentRunViewerScreen } from "./components/AgentRunViewerScreen";
import { AnalyticsScreen } from "./components/AnalyticsScreen";
import { SettingsScreen } from "./components/SettingsScreen";
import {
  JobInboxItem,
  JobDetailData,
  PendingProposalData,
  MessageThreadItem,
  AnalyticsData,
  LearnedMemoryItem,
  UserProfileData
} from "./types";

const API_BASE = typeof window !== "undefined" && window.location.origin.includes(":5173")
  ? "http://localhost:8000"
  : "";

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>("inbox");
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [jobs, setJobs] = useState<JobInboxItem[]>([]);
  const [loadingJobs, setLoadingJobs] = useState<boolean>(true);

  // Active view states
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [jobDetail, setJobDetail] = useState<JobDetailData | null>(null);
  const [activeRunJobId, setActiveRunJobId] = useState<string | null>(null);
  const [pendingProposal, setPendingProposal] = useState<PendingProposalData | null>(null);

  // Secondary views state
  const [pipelineBoard, setPipelineBoard] = useState<Record<string, any[]>>({});
  const [messageThreads, setMessageThreads] = useState<MessageThreadItem[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [memories, setMemories] = useState<LearnedMemoryItem[]>([]);

  // Fetch initial profile & jobs
  useEffect(() => {
    fetchProfile();
    fetchJobs();
    fetchPipeline();
    fetchMessages();
    fetchAnalytics();
    fetchMemories();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/user/profile`);
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
      }
    } catch (e) {
      console.error("API error", e);
    }
  };

  const fetchJobs = async () => {
    setLoadingJobs(true);
    try {
      const res = await fetch(`${API_BASE}/api/jobs/inbox?limit=25`);
      if (res.ok) {
        const data = await res.json();
        setJobs(data);
      }
    } catch (e) {
      console.error("API error", e);
    } finally {
      setLoadingJobs(false);
    }
  };

  const fetchPipeline = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/board`);
      if (res.ok) setPipelineBoard(await res.json());
    } catch (e) {}
  };

  const fetchMessages = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/messages/threads`);
      if (res.ok) setMessageThreads(await res.json());
    } catch (e) {}
  };

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/analytics`);
      if (res.ok) setAnalytics(await res.json());
    } catch (e) {}
  };

  const fetchMemories = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/memory`);
      if (res.ok) {
        const data = await res.json();
        setMemories(data.memories || []);
      }
    } catch (e) {}
  };

  const handleSwitchPersona = async (personaId: string) => {
    try {
      await fetch(`${API_BASE}/api/user/switch_persona?persona_id=${personaId}`, { method: "POST" });
      await fetchProfile();
      await fetchJobs();
    } catch (e) {}
  };

  const handleSelectJob = async (jobId: string) => {
    setSelectedJobId(jobId);
    try {
      const res = await fetch(`${API_BASE}/api/jobs/${jobId}/detail`);
      if (res.ok) {
        setJobDetail(await res.json());
        setCurrentTab("detail");
      }
    } catch (e) {}
  };

  const handleStartAgentRun = (jobId: string) => {
    setActiveRunJobId(jobId);
    setCurrentTab("stream");
  };

  const handleOpenStudio = async (threadId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/proposals/${threadId}/pending`);
      if (res.ok) {
        setPendingProposal(await res.json());
        setCurrentTab("studio");
      }
    } catch (e) {}
  };

  const handleResumeProposal = async (action: string, coverLetter: string, bidAmount: number) => {
    if (!pendingProposal) return;
    try {
      const res = await fetch(`${API_BASE}/api/proposals/${pendingProposal.thread_id}/resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, cover_letter: coverLetter, bid_amount: bidAmount })
      });
      if (res.ok) {
        await fetchProfile();
        await fetchPipeline();
        await fetchMemories();
        setCurrentTab("pipeline");
        setPendingProposal(null);
      }
    } catch (e) {}
  };

  const handleDeleteMemory = async (memoryId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/memory/${memoryId}`, { method: "DELETE" });
      if (res.ok) fetchMemories();
    } catch (e) {}
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        profile={profile}
        onSwitchPersona={handleSwitchPersona}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentTab === "inbox" && (
          <JobInboxScreen
            jobs={jobs}
            onSelectJob={handleSelectJob}
            onStartAgentRun={handleStartAgentRun}
            loading={loadingJobs}
          />
        )}

        {currentTab === "detail" && jobDetail && (
          <JobDetailScreen
            data={jobDetail}
            onBack={() => setCurrentTab("inbox")}
            onRunAgent={handleStartAgentRun}
          />
        )}

        {currentTab === "stream" && activeRunJobId && (
          <AgentRunViewerScreen
            jobId={activeRunJobId}
            onOpenStudio={handleOpenStudio}
            onBack={() => setCurrentTab("inbox")}
          />
        )}

        {currentTab === "studio" && pendingProposal && (
          <ProposalStudioScreen
            data={pendingProposal}
            onResume={handleResumeProposal}
            onBack={() => setCurrentTab("stream")}
          />
        )}

        {currentTab === "pipeline" && (
          <PipelineBoardScreen board={pipelineBoard} />
        )}

        {currentTab === "messages" && (
          <MessagesScreen threads={messageThreads} />
        )}

        {currentTab === "analytics" && analytics && (
          <AnalyticsScreen data={analytics} />
        )}

        {currentTab === "settings" && (
          <SettingsScreen
            profile={profile}
            memories={memories}
            onDeleteMemory={handleDeleteMemory}
          />
        )}
      </main>
    </div>
  );
};
