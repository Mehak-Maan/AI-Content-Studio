import React, { useEffect, useRef } from 'react';
import { 
  CheckCircle2, Loader2, AlertCircle, RefreshCw, Terminal, 
  Sparkles, Film, Mic, Music, Subtitles, Scissors, ShieldCheck, 
  FileText, Play 
} from 'lucide-react';

const AGENTS = [
  { id: 'Manager Agent', label: 'Manager Agent', desc: 'Understanding request & planning', icon: Sparkles },
  { id: 'Script Agent', label: 'Script Agent', desc: 'Writing hook, narration & scene script', icon: FileText },
  { id: 'Scene Agent', label: 'Scene Agent', desc: 'Directing camera, lighting & styles', icon: Film },
  { id: 'Video Generation Agent', label: 'Video Generation Agent', desc: 'Synthesizing scene video clips', icon: Film },
  { id: 'Voice Agent', label: 'Voice Agent', desc: 'Generating neural voice-over', icon: Mic },
  { id: 'Audio Agent', label: 'Audio Agent', desc: 'Synthesizing background music', icon: Music },
  { id: 'Subtitle Agent', label: 'Subtitle Agent', desc: 'Creating synced SRT subtitles', icon: Subtitles },
  { id: 'Editor Agent', label: 'Editor Agent', desc: 'FFmpeg mixing, subtitles & rendering', icon: Scissors },
  { id: 'Reviewer Agent', label: 'Reviewer Agent', desc: 'Media stream validation & QA', icon: ShieldCheck },
];

export default function GenerationProgress({ 
  project, 
  progress, 
  currentAgent, 
  status, 
  message, 
  logs = [], 
  onViewResult, 
  onRegenerate 
}) {
  const terminalRef = useRef(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  // Determine status of each agent in pipeline
  const getAgentStatus = (agentId) => {
    if (status === 'completed') return 'completed';
    if (status === 'failed' && currentAgent === agentId) return 'failed';
    
    const currentIndex = AGENTS.findIndex(a => a.id === currentAgent);
    const thisIndex = AGENTS.findIndex(a => a.id === agentId);

    if (thisIndex < currentIndex) return 'completed';
    if (thisIndex === currentIndex) return status === 'running' ? 'running' : 'completed';
    return 'waiting';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn pb-12">
      {/* Header Info */}
      <div className="glass-panel p-6 rounded-3xl border border-indigo-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold border border-indigo-500/30">
              Project #{project?.id || '---'}
            </span>
            <span className="text-xs text-slate-400 capitalize">{project?.video_type?.replace('_', ' ')} • {project?.duration}s</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">{project?.title || 'AI Multi-Agent Production Pipeline'}</h2>
        </div>

        {status === 'completed' && (
          <button
            onClick={onViewResult}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-cyan-500 hover:from-emerald-500 hover:to-cyan-400 text-white font-semibold text-sm shadow-lg shadow-emerald-500/25 transition-all transform hover:scale-105"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>View Final Video</span>
          </button>
        )}

        {status === 'failed' && (
          <button
            onClick={onRegenerate}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-sm shadow-md transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Retry Pipeline</span>
          </button>
        )}
      </div>

      {/* Progress Bar Card */}
      <div className="glass-card p-6 rounded-2xl border border-studio-border space-y-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            {status === 'running' && <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />}
            {status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
            {status === 'failed' && <AlertCircle className="w-4 h-4 text-rose-400" />}
            <span className="font-semibold text-white">
              {status === 'completed' ? 'Video Generation Finished!' : (message || `${currentAgent || 'Manager'} in progress...`)}
            </span>
          </div>
          <span className="font-mono font-bold text-indigo-400 text-base">{progress}%</span>
        </div>

        <div className="w-full h-3 bg-studio-bg rounded-full overflow-hidden p-0.5 border border-studio-border">
          <div 
            className="h-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 rounded-full transition-all duration-500 shadow-md shadow-cyan-500/30"
            style={{ width: `${Math.min(100, Math.max(5, progress))}%` }}
          />
        </div>
      </div>

      {/* Agents Pipeline Grid */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Multi-Agent Pipeline</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {AGENTS.map((agent, idx) => {
            const agentStatus = getAgentStatus(agent.id);
            const Icon = agent.icon;

            return (
              <div
                key={agent.id}
                className={`p-4 rounded-2xl border transition-all ${
                  agentStatus === 'running'
                    ? 'bg-indigo-950/40 border-indigo-500 shadow-lg shadow-indigo-500/20 ring-1 ring-indigo-500/50'
                    : agentStatus === 'completed'
                    ? 'bg-studio-panel/80 border-emerald-500/30'
                    : agentStatus === 'failed'
                    ? 'bg-rose-950/30 border-rose-500/40'
                    : 'bg-studio-card/50 border-studio-border/50 opacity-60'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                      agentStatus === 'running'
                        ? 'bg-indigo-600 text-white animate-pulse'
                        : agentStatus === 'completed'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : agentStatus === 'failed'
                        ? 'bg-rose-500/20 text-rose-400'
                        : 'bg-studio-bg text-slate-500'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">{agent.label}</div>
                      <div className="text-[11px] text-slate-400 line-clamp-1">{agent.desc}</div>
                    </div>
                  </div>

                  {/* Status indicator */}
                  <div>
                    {agentStatus === 'completed' && (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    )}
                    {agentStatus === 'running' && (
                      <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                    )}
                    {agentStatus === 'failed' && (
                      <AlertCircle className="w-4 h-4 text-rose-400" />
                    )}
                    {agentStatus === 'waiting' && (
                      <span className="text-[10px] font-mono text-slate-600">#{idx + 1}</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Terminal Real-Time Agent Logs */}
      <div className="glass-card rounded-2xl border border-studio-border overflow-hidden">
        <div className="px-4 py-3 bg-studio-bg/90 border-b border-studio-border flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span>Agent Orchestration Logs</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">Live Stream</span>
        </div>

        <div 
          ref={terminalRef}
          className="p-4 bg-[#07090E] font-mono text-xs text-slate-300 h-56 overflow-y-auto space-y-1.5"
        >
          {logs.length === 0 ? (
            <div className="text-slate-600 italic">Waiting for agent activity...</div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="leading-relaxed flex items-start gap-2">
                <span className="text-slate-600 select-none">[{log.timestamp ? log.timestamp.split('T')[1]?.slice(0, 8) : '00:00:00'}]</span>
                <span className={`font-bold ${
                  log.agent?.includes('Video') ? 'text-indigo-400' :
                  log.agent?.includes('Voice') ? 'text-cyan-400' :
                  log.agent?.includes('Audio') ? 'text-amber-400' :
                  log.agent?.includes('Editor') ? 'text-purple-400' :
                  log.agent?.includes('Reviewer') ? 'text-emerald-400' : 'text-blue-400'
                }`}>
                  [{log.agent || 'System'}]
                </span>
                <span className={log.level === 'ERROR' ? 'text-rose-400 font-semibold' : log.level === 'WARNING' ? 'text-amber-300' : 'text-slate-300'}>
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
