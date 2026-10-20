import { useState, useCallback, useEffect } from 'react';
import TabBar from './components/TabBar';
import ToastContainer from './components/Toast';
import SettingsModal from './components/SettingsModal';
import DynastyFilter from './components/tab1-dynasty/DynastyFilter';
import SilkRoadMap from './components/tab2-silkroad/SilkRoadMap';
import StoryGenerator from './components/tab3-story/StoryGenerator';
import { hasImageKey } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dynasty');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [keyReady, setKeyReady] = useState(() => hasImageKey());

  // Keep the "no key" hint in sync with the settings panel / other tabs
  useEffect(() => {
    const sync = () => setKeyReady(hasImageKey());
    window.addEventListener('jade:settings', sync);
    const openSettings = () => setSettingsOpen(true);
    window.addEventListener('jade:open-settings', openSettings);
    return () => {
      window.removeEventListener('jade:settings', sync);
      window.removeEventListener('jade:open-settings', openSettings);
    };
  }, []);

  const renderTab = useCallback(() => {
    switch (activeTab) {
      case 'dynasty': return <DynastyFilter />;
      case 'silkroad': return <SilkRoadMap />;
      case 'story': return <StoryGenerator />;
      default: return null;
    }
  }, [activeTab]);

  return (
    <div className="h-screen flex flex-col bg-bg">
      {/* Header */}
      <header className="flex-shrink-0 pt-3 pb-2 px-4 text-center border-b border-border/50 bg-bg/95 backdrop-blur-sm z-10 relative">
        <h1 className="font-display text-lg font-bold text-fg-primary tracking-wide">
          {activeTab === 'dynasty' && '朝代滤镜'}
          {activeTab === 'silkroad' && '丝路玉路'}
          {activeTab === 'story' && '玉文化典故'}
        </h1>
        <p className="text-[11px] text-fg-tertiary mt-0.5">
          {activeTab === 'dynasty' && '分级选择，组合专属玉器设计'}
          {activeTab === 'silkroad' && '全球玉文化交流史探索'}
          {activeTab === 'story' && '生成可分享的典故卡片'}
        </p>

        {/* Settings — bring your own API key */}
        <button
          onClick={() => setSettingsOpen(true)}
          title="模型 API Key 设置"
          className="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 flex items-center justify-center rounded-full bg-card border border-border text-sm active:scale-95 transition-transform"
        >
          ⚙️
          {!keyReady && (
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-seal" />
          )}
        </button>
      </header>

      {/* No-key hint */}
      {!keyReady && activeTab === 'dynasty' && (
        <button
          onClick={() => setSettingsOpen(true)}
          className="flex-shrink-0 mx-4 mt-2 px-3 py-2 rounded-xl bg-gold/10 border border-gold/25 text-[11px] text-gold text-left leading-relaxed"
        >
          🔑 未配置图片 API Key — 点击填写即可生成玉器（典故与地图功能不受影响）
        </button>
      )}

      {/* Tab content */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden pb-16">
        <div className="animate-[fadeIn_.25s_ease-out]" key={activeTab}>
          {renderTab()}
        </div>
      </main>

      {/* Bottom tab bar */}
      <TabBar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Global toast */}
      <ToastContainer />

      {settingsOpen && <SettingsModal onClose={() => setSettingsOpen(false)} />}
    </div>
  );
}
