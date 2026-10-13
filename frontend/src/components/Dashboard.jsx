import React from 'react';
import { 
  Film, Sparkles, Clock, CheckCircle2, AlertCircle, Play, 
  Trash2, Plus, ArrowRight, Layers, Music, Mic, RefreshCw 
} from 'lucide-react';
import { api } from '../services/api';

export default function Dashboard({ 
  projects, 
  loading, 
  onSelectProject, 
  onNavigateCreate, 
  onDeleteProject,
  onRefresh 
}) {
  const totalProjects = projects.length;
  const completedProjects = projects.filter(p => p.status === 'completed').length;
  const runningProjects = projects.filter(p => p.status === 'running').length;
  const draftProjects = projects.filter(p => p.status === 'draft').length;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl glass-panel p-8 sm:p-10 border border-indigo-500/20 bg-gradient-to-r from-indigo-950/40 via-studio-panel to-slate-900/60 shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Autonomous Multi-Agent Orchestration</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
            AI Content Studio
          </h1>
          <p className="text-slate-300 text-base sm:text-lg max-w-2xl leading-relaxed">
            Create high-retention videos, neural voice-overs, and background audio with autonomous AI agents. 
            From prompt to final polished MP4 in minutes.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-4">
            <button
              onClick={onNavigateCreate}
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white font-semibold text-sm shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Plus className="w-4 h-4" />
              <span>+ Create Video</span>
            </button>

            <button
              onClick={onRefresh}
              className="flex items-center gap-2 px-4 py-3.5 rounded-xl bg-studio-card hover:bg-studio-panel border border-studio-border text-slate-300 hover:text-white text-sm font-medium transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="glass-card p-5 rounded-2xl border border-studio-border flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{totalProjects}</div>
            <div className="text-xs font-medium text-slate-400">Total Projects</div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-studio-border flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{completedProjects}</div>
            <div className="text-xs font-medium text-slate-400">Videos Generated</div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-studio-border flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Film className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">{runningProjects}</div>
            <div className="text-xs font-medium text-slate-400">Processing</div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-studio-border flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">9 Agents</div>
            <div className="text-xs font-medium text-slate-400">LangGraph Ready</div>
          </div>
        </div>
      </div>

      {/* Recent Projects Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Recent Projects</h2>
            <p className="text-xs text-slate-400">Manage and preview your multi-agent video generations</p>
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p>Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="glass-panel rounded-2xl p-12 text-center space-y-4 border border-dashed border-studio-border">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto">
              <Film className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-white">No projects created yet</h3>
              <p className="text-sm text-slate-400 max-w-sm mx-auto">
                Generate your first multi-agent AI video with script, scenes, neural voice-over, and music.
              </p>
            </div>
            <button
              onClick={onNavigateCreate}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Create First Video</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((proj) => (
              <div
                key={proj.id}
                className="glass-card glass-card-hover rounded-2xl overflow-hidden border border-studio-border flex flex-col group"
              >
                {/* Thumbnail / Video Preview Area */}
                <div 
                  onClick={() => onSelectProject(proj)}
                  className="relative aspect-video bg-slate-950 flex items-center justify-center overflow-hidden cursor-pointer"
                >
                  {proj.thumbnail_path ? (
                    <img 
                      src={api.getThumbnailUrl(proj.id)} 
                      alt={proj.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  ) : null}

                  {/* Overlay Gradient */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent pointer-events-none" />

                  {/* Play icon badge */}
                  {proj.status === 'completed' ? (
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                      <div className="w-12 h-12 rounded-full bg-indigo-600/90 text-white flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform">
                        <Play className="w-5 h-5 ml-0.5 fill-white" />
                      </div>
                    </div>
                  ) : proj.status === 'running' ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/60">
                      <div className="text-center space-y-2">
                        <div className="w-8 h-8 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto" />
                        <span className="text-xs text-indigo-300 font-medium">Generating...</span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-slate-500 flex flex-col items-center gap-1">
                      <Film className="w-8 h-8" />
                      <span className="text-[11px]">Ready to Generate</span>
                    </div>
                  )}

                  {/* Badges */}
                  <div className="absolute top-3 left-3 flex gap-1.5">
                    <span className="px-2 py-0.5 rounded-md bg-black/60 backdrop-blur-md text-[10px] font-semibold text-white border border-white/10 uppercase">
                      {proj.aspect_ratio}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-black/60 backdrop-blur-md text-[10px] font-semibold text-slate-300 border border-white/10">
                      {proj.duration}s
                    </span>
                  </div>

                  <div className="absolute top-3 right-3">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${
                      proj.status === 'completed'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                        : proj.status === 'running'
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30 animate-pulse'
                        : proj.status === 'failed'
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                        : 'bg-slate-700/50 text-slate-300 border-slate-600/30'
                    }`}>
                      {proj.status.toUpperCase()}
                    </span>
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-5 flex-1 flex flex-col justify-between space-y-3">
                  <div className="space-y-1.5">
                    <h3 
                      onClick={() => onSelectProject(proj)}
                      className="text-base font-bold text-white group-hover:text-indigo-400 transition-colors cursor-pointer line-clamp-1"
                    >
                      {proj.title}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                      {proj.prompt}
                    </p>
                  </div>

                  {/* Meta Tags */}
                  <div className="flex items-center gap-3 text-xs text-slate-400 pt-2 border-t border-studio-border/60">
                    <span className="capitalize">{proj.video_type?.replace('_', ' ')}</span>
                    <span>•</span>
                    <span>{proj.language}</span>
                    <span>•</span>
                    <span>{new Date(proj.created_at).toLocaleDateString()}</span>
                  </div>

                  {/* Card Actions */}
                  <div className="flex items-center justify-between pt-2">
                    <button
                      onClick={() => onSelectProject(proj)}
                      className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                    >
                      <span>Open Studio</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Delete this video project?')) {
                          onDeleteProject(proj.id);
                        }
                      }}
                      className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                      title="Delete Project"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
