import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import CreateVideo from './components/CreateVideo';
import GenerationProgress from './components/GenerationProgress';
import VideoResult from './components/VideoResult';
import SettingsModal from './components/SettingsModal';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'create' | 'progress' | 'result'
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // Real-time generation state
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentAgent, setCurrentAgent] = useState('Manager Agent');
  const [generationStatus, setGenerationStatus] = useState('waiting');
  const [statusMessage, setStatusMessage] = useState('');
  const [agentLogs, setAgentLogs] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  const socketRef = useRef(null);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    fetchProjects();

    // Setup WebSocket
    const socket = api.connectWebSocket(
      (msg) => {
        if (msg.event === 'status') {
          handleStatusEvent(msg.data);
        } else if (msg.event === 'log') {
          handleLogEvent(msg.data);
        }
      },
      () => setWsConnected(true),
      () => setWsConnected(false)
    );
    socketRef.current = socket;

    return () => {
      if (socketRef.current) socketRef.current.close();
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  const handleStatusEvent = (event) => {
    if (event.project_id && selectedProject && event.project_id === selectedProject.id) {
      if (event.progress !== undefined) setCurrentProgress(event.progress);
      if (event.agent) setCurrentAgent(event.agent);
      if (event.status) setGenerationStatus(event.status);
      if (event.message) setStatusMessage(event.message);

      if (event.status === 'completed') {
        // Refresh project data and transition to result
        fetchProject(selectedProject.id).then(updated => {
          if (updated) {
            setSelectedProject(updated);
            fetchProjects();
            setActiveTab('result');
          }
        });
      }
    }
  };

  const handleLogEvent = (log) => {
    if (!selectedProject || !log.project_id || log.project_id === selectedProject.id) {
      setAgentLogs(prev => [...prev.slice(-150), log]);
    }
  };

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await api.getProjects();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProject = async (id) => {
    try {
      const proj = await api.getProject(id);
      return proj;
    } catch (err) {
      console.error('Failed to fetch project details:', err);
      return null;
    }
  };

  // Create & Start Video Generation Workflow
  const handleCreateProject = async (formData) => {
    setIsSubmitting(true);
    try {
      // Step 1: Create project in DB
      const project = await api.createProject(formData);
      setSelectedProject(project);
      
      // Step 2: Switch to progress pipeline
      setCurrentProgress(5);
      setCurrentAgent('Manager Agent');
      setGenerationStatus('running');
      setStatusMessage('Initializing autonomous agent pipeline...');
      setAgentLogs([]);
      setActiveTab('progress');

      // Step 3: Trigger generation
      await api.startGeneration(project.id);
      
      // Start fallback polling in case WS is interrupted
      startPolling(project.id);
      fetchProjects();
    } catch (err) {
      alert('Error starting video generation: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const startPolling = (projectId) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    
    pollIntervalRef.current = setInterval(async () => {
      try {
        const status = await api.getGenerationStatus(projectId);
        setCurrentProgress(status.progress || 0);
        setCurrentAgent(status.current_agent || 'Manager Agent');
        setGenerationStatus(status.status);
        if (status.message) setStatusMessage(status.message);

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollIntervalRef.current);
          const updated = await fetchProject(projectId);
          if (updated) {
            setSelectedProject(updated);
            fetchProjects();
            if (status.status === 'completed') {
              setActiveTab('result');
            }
          }
        }
      } catch (e) {
        console.warn('Polling status error:', e);
      }
    }, 2500);
  };

  const handleSelectProject = async (project) => {
    const fullProject = await fetchProject(project.id);
    setSelectedProject(fullProject || project);
    
    if (project.status === 'completed') {
      setActiveTab('result');
    } else if (project.status === 'running') {
      setCurrentProgress(project.progress || 20);
      setCurrentAgent(project.current_agent || 'Manager Agent');
      setGenerationStatus(project.status);
      startPolling(project.id);
      setActiveTab('progress');
    } else {
      setActiveTab('result');
    }
  };

  const handleRegenerateProject = async (projectId) => {
    setIsRegenerating(true);
    try {
      setGenerationStatus('running');
      setCurrentProgress(5);
      setCurrentAgent('Manager Agent');
      setStatusMessage('Regenerating video...');
      setAgentLogs([]);
      setActiveTab('progress');

      await api.regenerateProject(projectId);
      startPolling(projectId);
      fetchProjects();
    } catch (err) {
      alert('Error regenerating project: ' + err.message);
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleRegenerateScene = async (projectId, sceneId) => {
    try {
      await api.regenerateScene(projectId, sceneId);
      // Refresh project to load updated scene and final video
      const updated = await fetchProject(projectId);
      if (updated) {
        setSelectedProject(updated);
        fetchProjects();
      }
    } catch (err) {
      alert('Error regenerating scene: ' + err.message);
    }
  };

  const handleDeleteProject = async (projectId) => {
    try {
      await api.deleteProject(projectId);
      setProjects(prev => prev.filter(p => p.id !== projectId));
      if (selectedProject?.id === projectId) {
        setSelectedProject(null);
        setActiveTab('dashboard');
      }
    } catch (err) {
      alert('Error deleting project: ' + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-studio-bg text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSettings={() => setIsSettingsOpen(true)}
        wsConnected={wsConnected}
      />

      {/* Main App Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {activeTab === 'dashboard' && (
          <Dashboard
            projects={projects}
            loading={loading}
            onSelectProject={handleSelectProject}
            onNavigateCreate={() => setActiveTab('create')}
            onDeleteProject={handleDeleteProject}
            onRefresh={fetchProjects}
          />
        )}

        {activeTab === 'create' && (
          <CreateVideo
            onSubmit={handleCreateProject}
            isSubmitting={isSubmitting}
          />
        )}

        {activeTab === 'progress' && (
          <GenerationProgress
            project={selectedProject}
            progress={currentProgress}
            currentAgent={currentAgent}
            status={generationStatus}
            message={statusMessage}
            logs={agentLogs}
            onViewResult={() => setActiveTab('result')}
            onRegenerate={() => selectedProject && handleRegenerateProject(selectedProject.id)}
          />
        )}

        {activeTab === 'result' && selectedProject && (
          <VideoResult
            project={selectedProject}
            onRegenerateProject={handleRegenerateProject}
            onRegenerateScene={handleRegenerateScene}
            isRegenerating={isRegenerating}
          />
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-studio-border/60 py-6 text-center text-xs text-slate-500">
        <p>AI Content Studio • Multi-Agent Autonomous Orchestration Engine (LangGraph + FastAPI + FFmpeg + Edge-TTS + React)</p>
      </footer>
    </div>
  );
}
