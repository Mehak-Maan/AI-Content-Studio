import React from 'react';
import { Video, PlusCircle, LayoutDashboard, Settings as SettingsIcon, Sparkles, Activity } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onOpenSettings, wsConnected }) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-studio-border bg-studio-bg/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setActiveTab('dashboard')} 
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
            <Video className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">AI Content Studio</span>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-full">
                Multi-Agent
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Video & Audio Engine</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-studio-card/80 p-1.5 rounded-xl border border-studio-border/60">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'dashboard'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => setActiveTab('create')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'create'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
            }`}
          >
            <PlusCircle className="w-4 h-4" />
            <span>Create Video</span>
          </button>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* Real-time WS Status Indicator */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-studio-panel border border-studio-border text-xs text-slate-300">
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span>{wsConnected ? 'Agents Online' : 'Connecting'}</span>
          </div>

          <button
            onClick={onOpenSettings}
            className="p-2.5 rounded-xl bg-studio-card hover:bg-studio-panel border border-studio-border text-slate-300 hover:text-white transition-colors"
            title="Settings & API Keys"
          >
            <SettingsIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
