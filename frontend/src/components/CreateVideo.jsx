import React, { useState } from 'react';
import { 
  Sparkles, Clock, Layout, Globe, Mic, Palette, Music, 
  Subtitles, ArrowRight, Wand2, Lightbulb 
} from 'lucide-react';

const EXAMPLE_PROMPTS = [
  "Create a 30-second Instagram Reel explaining what AI agents are in simple language.",
  "Create a professional advertisement for an AI automation company.",
  "Create a 60-second educational video explaining RAG architecture.",
  "Create a motivational short video about learning AI.",
  "Create a product promotion video for an AI SaaS platform."
];

const VIDEO_TYPES = [
  { id: 'instagram_reel', label: 'Instagram Reel' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'youtube_short', label: 'YouTube Short' },
  { id: 'youtube_video', label: 'YouTube Video' },
  { id: 'advertisement', label: 'Advertisement' },
  { id: 'educational_video', label: 'Educational Video' },
  { id: 'product_promotion', label: 'Product Promotion' },
  { id: 'story', label: 'Story' },
  { id: 'explainer', label: 'Explainer' },
  { id: 'social_media_marketing', label: 'Social Marketing' },
];

const ASPECT_RATIOS = [
  { id: '9:16', label: '9:16', desc: 'Reels, Shorts, TikTok' },
  { id: '16:9', label: '16:9', desc: 'YouTube, Web' },
  { id: '1:1', label: '1:1', desc: 'Square Feed' },
];

const VISUAL_STYLES = [
  'Cinematic', 'Modern', 'Minimal', 'Realistic', '3D', 'Cartoon', 'Corporate'
];

const VOICE_TONES = [
  'Professional', 'Friendly', 'Energetic', 'Narrator'
];

const MUSIC_GENRES = [
  'Cinematic', 'Technology', 'Energetic', 'Calm', 'None'
];

const LANGUAGES = [
  'English', 'Urdu', 'Roman Urdu', 'Hindi'
];

export default function CreateVideo({ onSubmit, isSubmitting }) {
  const [prompt, setPrompt] = useState('');
  const [videoType, setVideoType] = useState('instagram_reel');
  const [duration, setDuration] = useState(30);
  const [customDuration, setCustomDuration] = useState('');
  const [aspectRatio, setAspectRatio] = useState('9:16');
  const [language, setLanguage] = useState('English');
  const [voicePreference, setVoicePreference] = useState('Professional');
  const [visualStyle, setVisualStyle] = useState('Cinematic');
  const [musicPreference, setMusicPreference] = useState('Cinematic');
  const [captionsEnabled, setCaptionsEnabled] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const finalDuration = customDuration ? parseInt(customDuration, 10) : duration;

    onSubmit({
      prompt: prompt.trim(),
      video_type: videoType,
      duration: finalDuration || 30,
      aspect_ratio: aspectRatio,
      language,
      voice_preference: voicePreference,
      visual_style: visualStyle.toLowerCase(),
      music_preference: musicPreference,
      captions_enabled: captionsEnabled
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn pb-12">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Create AI Video</h1>
        <p className="text-slate-400 text-sm max-w-xl mx-auto">
          Configure your autonomous multi-agent production team. Enter your vision and let the agents research, script, direct, voice, and render.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Prompt Input Box */}
        <div className="glass-panel p-6 rounded-3xl border border-indigo-500/20 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>Describe the video you want to create</span>
            </label>
            <span className="text-xs text-slate-400">Natural language prompt</span>
          </div>

          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Create a 30-second Instagram Reel explaining what AI agents are in simple language with energetic narration and modern visuals..."
            rows={4}
            required
            className="w-full bg-studio-bg/90 border border-studio-border focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-2xl p-4 text-slate-100 placeholder-slate-500 text-sm leading-relaxed outline-none transition-all resize-none"
          />

          {/* Prompt quick templates */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center gap-1.5 text-xs font-medium text-slate-400">
              <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
              <span>Try an example prompt:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((ex, i) => (
                <button
                  type="button"
                  key={i}
                  onClick={() => setPrompt(ex)}
                  className="text-xs bg-studio-card hover:bg-studio-panel border border-studio-border hover:border-indigo-500/40 text-slate-300 hover:text-white px-3 py-1.5 rounded-xl text-left transition-colors"
                >
                  "{ex.slice(0, 48)}..."
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Video Production Parameters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Video Type */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Layout className="w-3.5 h-3.5 text-indigo-400" />
              <span>Video Type</span>
            </label>
            <select
              value={videoType}
              onChange={(e) => setVideoType(e.target.value)}
              className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-indigo-500"
            >
              {VIDEO_TYPES.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          {/* Aspect Ratio */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Layout className="w-3.5 h-3.5 text-cyan-400" />
              <span>Aspect Ratio</span>
            </label>
            <div className="grid grid-cols-3 gap-2">
              {ASPECT_RATIOS.map((ar) => (
                <button
                  type="button"
                  key={ar.id}
                  onClick={() => setAspectRatio(ar.id)}
                  className={`p-2.5 rounded-xl border text-center transition-all ${
                    aspectRatio === ar.id
                      ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30 font-semibold'
                      : 'bg-studio-bg border-studio-border text-slate-400 hover:text-white hover:bg-studio-panel'
                  }`}
                >
                  <div className="text-sm">{ar.label}</div>
                  <div className="text-[10px] opacity-75">{ar.desc.split(',')[0]}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Duration */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Duration</span>
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[15, 30, 60].map((d) => (
                <button
                  type="button"
                  key={d}
                  onClick={() => {
                    setDuration(d);
                    setCustomDuration('');
                  }}
                  className={`py-2 rounded-xl border text-sm font-medium transition-all ${
                    duration === d && !customDuration
                      ? 'bg-indigo-600 text-white border-indigo-500 shadow-md'
                      : 'bg-studio-bg border-studio-border text-slate-400 hover:text-white'
                  }`}
                >
                  {d}s
                </button>
              ))}
              <input
                type="number"
                placeholder="Custom"
                value={customDuration}
                onChange={(e) => setCustomDuration(e.target.value)}
                min="5"
                max="180"
                className={`px-2 py-1 text-center bg-studio-bg border rounded-xl text-xs text-slate-200 outline-none ${
                  customDuration ? 'border-indigo-500 ring-1 ring-indigo-500' : 'border-studio-border'
                }`}
              />
            </div>
          </div>

          {/* Language */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Globe className="w-3.5 h-3.5 text-emerald-400" />
              <span>Language</span>
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-indigo-500"
            >
              {LANGUAGES.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>

          {/* Voice Preference */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Mic className="w-3.5 h-3.5 text-rose-400" />
              <span>Voice Tone</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              {VOICE_TONES.map((vt) => (
                <button
                  type="button"
                  key={vt}
                  onClick={() => setVoicePreference(vt)}
                  className={`py-2 px-3 rounded-xl border text-xs font-medium transition-all ${
                    voicePreference === vt
                      ? 'bg-indigo-600 text-white border-indigo-500'
                      : 'bg-studio-bg border-studio-border text-slate-400 hover:text-white'
                  }`}
                >
                  {vt}
                </button>
              ))}
            </div>
          </div>

          {/* Visual Style */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Palette className="w-3.5 h-3.5 text-purple-400" />
              <span>Visual Style</span>
            </label>
            <select
              value={visualStyle}
              onChange={(e) => setVisualStyle(e.target.value)}
              className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-indigo-500"
            >
              {VISUAL_STYLES.map((vs) => (
                <option key={vs} value={vs}>
                  {vs}
                </option>
              ))}
            </select>
          </div>

          {/* Music Preference */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border space-y-3">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Music className="w-3.5 h-3.5 text-amber-400" />
              <span>Background Music</span>
            </label>
            <select
              value={musicPreference}
              onChange={(e) => setMusicPreference(e.target.value)}
              className="w-full bg-studio-bg border border-studio-border rounded-xl px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-indigo-500"
            >
              {MUSIC_GENRES.map((mg) => (
                <option key={mg} value={mg}>
                  {mg}
                </option>
              ))}
            </select>
          </div>

          {/* Captions Toggle */}
          <div className="glass-panel p-5 rounded-2xl border border-studio-border flex items-center justify-between">
            <div className="space-y-1">
              <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Subtitles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Burn Subtitles</span>
              </div>
              <p className="text-[11px] text-slate-400">Add synchronized dynamic social captions</p>
            </div>
            <button
              type="button"
              onClick={() => setCaptionsEnabled(!captionsEnabled)}
              className={`w-12 h-6 flex items-center rounded-full p-1 transition-colors ${
                captionsEnabled ? 'bg-indigo-600 justify-end' : 'bg-slate-700 justify-start'
              }`}
            >
              <div className="bg-white w-4 h-4 rounded-full shadow-md transform transition-transform" />
            </button>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={isSubmitting || !prompt.trim()}
            className={`w-full py-4 rounded-2xl font-bold text-base flex items-center justify-center gap-3 text-white transition-all shadow-xl shadow-indigo-600/30 ${
              isSubmitting || !prompt.trim()
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-studio-border'
                : 'bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 hover:scale-[1.01] active:scale-[0.99]'
            }`}
          >
            {isSubmitting ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Dispatching Multi-Agent Workflow...</span>
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5 text-cyan-200" />
                <span>GENERATE VIDEO</span>
                <ArrowRight className="w-5 h-5 text-cyan-200" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
