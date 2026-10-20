const TABS = [
  { id: 'dynasty', icon: '📷', label: '朝代滤镜' },
  { id: 'silkroad', icon: '🗺️', label: '丝路玉路' },
  { id: 'story', icon: '📜', label: '典故生成' },
];

export default function TabBar({ activeTab, onTabChange }) {
  return (
    <nav className="tab-bar fixed bottom-0 inset-x-0 z-[1000] bg-card/95 backdrop-blur-xl border-t border-border safe-bottom">
      <div className="flex items-center justify-around h-14 max-w-lg mx-auto">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`tab-btn flex flex-col items-center gap-0.5 px-4 py-1.5 min-w-[72px] rounded-xl transition-all duration-200 ${
                isActive
                  ? 'text-jade scale-105'
                  : 'text-fg-tertiary hover:text-fg-secondary active:scale-95'
              }`}
            >
              <span className={`text-xl transition-transform duration-300 ${isActive ? 'scale-110 -translate-y-0.5' : ''}`}>
                {tab.icon}
              </span>
              <span className={`text-[11px] font-medium ${isActive ? 'text-jade' : ''}`}>
                {tab.label}
              </span>
              {isActive && (
                <span className="w-1 h-1 rounded-full bg-jade mt-0.5 animate-pulse" />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
