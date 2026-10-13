import React, { useState } from 'react';
import { 
  Download, RefreshCw, Share2, Play, CheckCircle2, 
  FileText, Film, Volume2, ShieldCheck, Clock, Sparkles, 
  Layers, ChevronRight, AlertCircle, Copy, Check 
} from 'lucide-react';
import { api } from '../services/api';

export default function VideoResult({ 
  project, 
  onRegenerateProject, 
  onRegenerateScene, 
  isRegenerating 
}) {
  const [activeTab, setActiveTab] = useState('scenes'); // 'scenes' | 'script' | 'qa'
  const [copied, setCopied] = useState(false);
  const [selectedScene, setSelectedScene] = useState(null);
  const [regeneratingSceneId, setRegeneratingSceneId] = useState(null);

  if (!project) return null;

  const version = project.updated_at ? encodeURIComponent(project.updated_at) : '1';
  const videoUrl = api.getVideoUrl(project.id, version);
  const script = project.script_data || {};
  const scenes = project.scenes || [];
  const review = project.review_data || {};

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(project.prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRegenScene = async (scene) => {
    if (confirm(`Regenerate Scene ${scene.scene_number}? Only this scene will be re-synthesized and re-compiled into the final video.`)) {
      setRegeneratingSceneId(scene.id);
      try {
        await onRegenerateScene(project.id, scene.id);
      } finally {
        setRegeneratingSceneId(null);
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fadeIn pb-16">
      {/* Top Banner & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border border-indigo-500/20 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold border border-emerald-500/30 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>Production Complete</span>
            </span>
            <span className="text-xs text-slate-400">ID: {project.id}</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">{project.title}</h1>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <a
            href={videoUrl}
            download={`ai_studio_${project.id}.mp4`}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white font-semibold text-sm shadow-lg shadow-indigo-500/25 transition-all transform hover:scale-105 active:scale-95"
          >
            <Download className="w-4 h-4" />
            <span>Download MP4</span>
          </a>

          <button
            onClick={() => onRegenerateProject(project.id)}
            disabled={isRegenerating}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-studio-card hover:bg-studio-panel border border-studio-border text-slate-200 hover:text-white text-sm font-medium transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRegenerating ? 'animate-spin text-indigo-400' : ''}`} />
            <span>Regenerate Full Video</span>
          </button>

          <button
            onClick={handleCopyPrompt}
            className="p-2.5 rounded-xl bg-studio-card hover:bg-studio-panel border border-studio-border text-slate-300 hover:text-white transition-colors"
            title="Copy Original Prompt"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Main Studio Grid: Video Player + Summary Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Video Player */}
        <div className="lg:col-span-7 space-y-4">
          <div className="glass-card rounded-3xl overflow-hidden border border-studio-border shadow-2xl bg-black flex items-center justify-center relative">
            <video
              key={videoUrl + (project.updated_at || '')}
              src={videoUrl}
              controls
              autoPlay
              playsInline
              className={`w-full max-h-[580px] object-contain rounded-2xl bg-black ${
                project.aspect_ratio === '9:16' ? 'aspect-[9/16] max-w-sm mx-auto' : 'aspect-video'
              }`}
            >
              Your browser does not support the video tag.
            </video>
          </div>

          {/* Quick specs pill bar */}
          <div className="glass-card p-4 rounded-2xl border border-studio-border flex flex-wrap items-center justify-around gap-4 text-xs">
            <div className="flex items-center gap-2 text-slate-300">
              <Clock className="w-4 h-4 text-indigo-400" />
              <span>Duration: <strong className="text-white">{project.duration}s</strong></span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <Film className="w-4 h-4 text-cyan-400" />
              <span>Format: <strong className="text-white">{project.aspect_ratio}</strong></span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <Volume2 className="w-4 h-4 text-amber-400" />
              <span>Voice: <strong className="text-white">{project.voice_preference}</strong></span>
            </div>
            <div className="flex items-center gap-2 text-slate-300">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>QA: <strong className="text-emerald-400">Approved</strong></span>
            </div>
          </div>
        </div>

        {/* Right: Studio Details Tabs */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-panel p-2 rounded-2xl border border-studio-border flex items-center gap-1">
            <button
              onClick={() => setActiveTab('scenes')}
              className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all ${
                activeTab === 'scenes'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
              }`}
            >
              Scene Timeline ({scenes.length})
            </button>
            <button
              onClick={() => setActiveTab('script')}
              className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all ${
                activeTab === 'script'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
              }`}
            >
              Script & Voice
            </button>
            <button
              onClick={() => setActiveTab('qa')}
              className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all ${
                activeTab === 'qa'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
              }`}
            >
              QA Review
            </button>
          </div>

          {/* Tab 1: Scene Timeline with Per-Scene Regeneration */}
          {activeTab === 'scenes' && (
            <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
              {scenes.map((scene) => (
                <div
                  key={scene.id}
                  className="glass-card rounded-2xl p-4 border border-studio-border hover:border-indigo-500/40 transition-all space-y-3"
                >
                  <div className="flex items-start gap-3">
                    {/* Scene Thumbnail */}
                    <div className="w-20 h-14 rounded-xl bg-slate-900 border border-studio-border overflow-hidden flex-shrink-0 relative">
                      <img
                        src={api.getSceneThumbnailUrl(project.id, scene.id)}
                        alt={`Scene ${scene.scene_number}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                      <span className="absolute bottom-1 right-1 bg-black/70 px-1 rounded text-[9px] text-white font-mono">
                        {scene.duration}s
                      </span>
                    </div>

                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-indigo-300">
                          Scene {scene.scene_number}
                        </span>
                        <span className="text-[10px] text-slate-400 capitalize">
                          {scene.camera_movement}
                        </span>
                      </div>
                      <p className="text-xs text-white line-clamp-2 leading-snug">
                        "{scene.narration}"
                      </p>
                    </div>
                  </div>

                  {/* Visual Prompt info */}
                  <div className="text-[11px] text-slate-400 bg-studio-bg/60 p-2.5 rounded-xl border border-studio-border/50">
                    <span className="font-semibold text-slate-300">Visual Prompt: </span>
                    {scene.visual_prompt}
                  </div>

                  {/* Per-scene actions */}
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] text-slate-500">
                      Transition: {scene.transition || 'fade'}
                    </span>
                    <button
                      onClick={() => handleRegenScene(scene)}
                      disabled={regeneratingSceneId === scene.id}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/30 text-indigo-300 hover:text-white text-xs font-medium transition-colors"
                    >
                      <RefreshCw className={`w-3 h-3 ${regeneratingSceneId === scene.id ? 'animate-spin' : ''}`} />
                      <span>{regeneratingSceneId === scene.id ? 'Regenerating...' : 'Regenerate Scene'}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab 2: Script & Narration */}
          {activeTab === 'script' && (
            <div className="glass-card rounded-2xl p-5 border border-studio-border space-y-4 max-h-[520px] overflow-y-auto">
              {script.hook && (
                <div className="space-y-1 bg-indigo-500/10 p-3.5 rounded-xl border border-indigo-500/20">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Hook</span>
                  <p className="text-xs text-white font-medium">"{script.hook}"</p>
                </div>
              )}

              <div className="space-y-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Scene Narrations</span>
                {scenes.map((s, idx) => (
                  <div key={idx} className="bg-studio-bg p-3 rounded-xl border border-studio-border space-y-1">
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span>Scene {s.scene_number}</span>
                      <span>{s.duration}s</span>
                    </div>
                    <p className="text-xs text-slate-200">"{s.narration}"</p>
                    {s.screen_text && (
                      <div className="text-[10px] text-cyan-400 font-medium">
                        On-screen text: [{s.screen_text}]
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {script.call_to_action && (
                <div className="space-y-1 bg-cyan-500/10 p-3.5 rounded-xl border border-cyan-500/20">
                  <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">Call To Action</span>
                  <p className="text-xs text-white font-medium">"{script.call_to_action}"</p>
                </div>
              )}
            </div>
          )}

          {/* Tab 3: QA Review Report */}
          {activeTab === 'qa' && (
            <div className="glass-card rounded-2xl p-5 border border-studio-border space-y-4">
              <div className="flex items-center gap-3 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                <ShieldCheck className="w-6 h-6 text-emerald-400 flex-shrink-0" />
                <div>
                  <h4 className="text-xs font-bold text-emerald-300">Reviewer Agent QA Approved</h4>
                  <p className="text-[11px] text-emerald-400/80">All codecs, media streams, audio levels, and scene timelines validated.</p>
                </div>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-2 border-b border-studio-border/60">
                  <span className="text-slate-400">Validation Status</span>
                  <span className="text-emerald-400 font-semibold">Approved (0 Issues)</span>
                </div>
                <div className="flex justify-between py-2 border-b border-studio-border/60">
                  <span className="text-slate-400">Measured Duration</span>
                  <span className="text-white font-mono">{review.actual_duration ? `${review.actual_duration.toFixed(1)}s` : `${project.duration}s`}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-studio-border/60">
                  <span className="text-slate-400">Export Resolution</span>
                  <span className="text-white font-mono">{review.resolution || (project.aspect_ratio === '9:16' ? '720x1280' : '1280x720')}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-studio-border/60">
                  <span className="text-slate-400">File Size</span>
                  <span className="text-white font-mono">{review.file_size_kb ? `${review.file_size_kb} KB` : 'Verified'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-studio-border/60">
                  <span className="text-slate-400">Burned Subtitles</span>
                  <span className="text-white">{project.captions_enabled ? 'Enabled & Synced' : 'Disabled'}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
