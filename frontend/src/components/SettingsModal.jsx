import React, { useState, useEffect } from 'react';
import { X, Key, Shield, Check, ExternalLink, Save, RefreshCw, Cpu, Mic } from 'lucide-react';
import { api } from '../services/api';

export default function SettingsModal({ isOpen, onClose }) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  
  const [geminiKey, setGeminiKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [elevenlabsKey, setElevenlabsKey] = useState('');
  const [hfKey, setHfKey] = useState('');
  const [voiceProvider, setVoiceProvider] = useState('edge_tts');
  const [maxRetries, setMaxRetries] = useState(2);
  const [configStatus, setConfigStatus] = useState({});

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await api.getSettings();
      setConfigStatus(data);
      setVoiceProvider(data.default_voice_provider || 'edge_tts');
      setMaxRetries(data.max_retries || 2);
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);

    try {
      const payload = {
        default_voice_provider: voiceProvider,
        max_retries: parseInt(maxRetries, 10),
      };
      if (geminiKey.trim()) payload.gemini_api_key = geminiKey.trim();
      if (groqKey.trim()) payload.groq_api_key = groqKey.trim();
      if (elevenlabsKey.trim()) payload.elevenlabs_api_key = elevenlabsKey.trim();
      if (hfKey.trim()) payload.huggingface_api_key = hfKey.trim();

      const updated = await api.updateSettings(payload);
      setConfigStatus(updated);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert('Error updating settings: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel w-full max-w-xl rounded-3xl border border-indigo-500/20 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-6 border-b border-studio-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">API Keys & Provider Configuration</h2>
              <p className="text-xs text-slate-400">Configure free-tier AI model providers or use built-in engines</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-studio-panel transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSave} className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
          {savedSuccess && (
            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>Settings and API credentials updated successfully!</span>
            </div>
          )}

          {/* LLM Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                <span>LLM Providers (Free Tiers Supported)</span>
              </span>
            </div>

            {/* Google Gemini */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="font-semibold text-slate-300">
                  Google Gemini API Key
                  {configStatus.gemini_api_key_set && (
                    <span className="ml-2 text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">Configured</span>
                  )}
                </label>
                <a
                  href="https://aistudio.google.com/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 text-[11px]"
                >
                  <span>Get Free Key</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <input
                type="password"
                placeholder={configStatus.gemini_api_key_set ? "••••••••••••••••" : "Paste Gemini API Key (e.g. AIzaSy...)"}
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-slate-100 placeholder-slate-600 outline-none focus:border-indigo-500"
              />
            </div>

            {/* Groq */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="font-semibold text-slate-300">
                  Groq API Key (Llama 3.3 70B)
                  {configStatus.groq_api_key_set && (
                    <span className="ml-2 text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">Configured</span>
                  )}
                </label>
                <a
                  href="https://console.groq.com/"
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 text-[11px]"
                >
                  <span>Get Free Key</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <input
                type="password"
                placeholder={configStatus.groq_api_key_set ? "••••••••••••••••" : "Paste Groq API Key (e.g. gsk_...)"}
                value={groqKey}
                onChange={(e) => setGroqKey(e.target.value)}
                className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-slate-100 placeholder-slate-600 outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Text-to-Speech Settings */}
          <div className="space-y-4 pt-2 border-t border-studio-border/60">
            <span className="font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Mic className="w-3.5 h-3.5 text-rose-400" />
              <span>Voice / Text-to-Speech Engine</span>
            </span>

            <div className="space-y-1.5">
              <label className="font-semibold text-slate-300">Default TTS Provider</label>
              <select
                value={voiceProvider}
                onChange={(e) => setVoiceProvider(e.target.value)}
                className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-slate-200 outline-none focus:border-indigo-500"
              >
                <option value="edge_tts">Microsoft Edge Neural TTS (100% Free, Studio Quality, No Key Needed)</option>
                <option value="elevenlabs">ElevenLabs API</option>
              </select>
            </div>

            {voiceProvider === 'elevenlabs' && (
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="font-semibold text-slate-300">ElevenLabs API Key</label>
                  <a
                    href="https://elevenlabs.io/"
                    target="_blank"
                    rel="noreferrer"
                    className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 text-[11px]"
                  >
                    <span>Get Key</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                <input
                  type="password"
                  placeholder={configStatus.elevenlabs_api_key_set ? "••••••••••••••••" : "Paste ElevenLabs API Key"}
                  value={elevenlabsKey}
                  onChange={(e) => setElevenlabsKey(e.target.value)}
                  className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-slate-100 placeholder-slate-600 outline-none focus:border-indigo-500"
                />
              </div>
            )}
          </div>

          {/* Text-to-Video Settings */}
          <div className="space-y-4 pt-2 border-t border-studio-border/60">
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="font-semibold text-slate-300">
                  Hugging Face API Key (Optional Video Models)
                  {configStatus.huggingface_api_key_set && (
                    <span className="ml-2 text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">Configured</span>
                  )}
                </label>
                <a
                  href="https://huggingface.co/settings/tokens"
                  target="_blank"
                  rel="noreferrer"
                  className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1 text-[11px]"
                >
                  <span>Get Free Token</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <input
                type="password"
                placeholder={configStatus.huggingface_api_key_set ? "••••••••••••••••" : "Paste Hugging Face API Token (e.g. hf_...)"}
                value={hfKey}
                onChange={(e) => setHfKey(e.target.value)}
                className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-slate-100 placeholder-slate-600 outline-none focus:border-indigo-500"
              />
              <p className="text-[11px] text-slate-500">
                Note: When Hugging Face API key is omitted or free quota is busy, the studio uses the local high-fidelity procedural motion synthesizer.
              </p>
            </div>
          </div>

          {/* Max Retries */}
          <div className="space-y-1.5 pt-2 border-t border-studio-border/60">
            <label className="font-semibold text-slate-300">Reviewer Agent Max Retries</label>
            <input
              type="number"
              min="1"
              max="5"
              value={maxRetries}
              onChange={(e) => setMaxRetries(e.target.value)}
              className="w-full bg-studio-bg border border-studio-border rounded-xl p-3 text-slate-100 outline-none focus:border-indigo-500"
            />
          </div>

          {/* Modal Footer */}
          <div className="pt-4 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-studio-panel border border-studio-border font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-500/25 transition-all"
            >
              {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              <span>Save Configuration</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
