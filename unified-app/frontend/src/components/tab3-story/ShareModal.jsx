import { useState } from 'react';
import { showToast } from '../Toast';

export default function ShareModal({ story, qrUrl, onClose }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const text = `【玉文化典故】${story.title}\n\n${story.explanation}\n\n——${story.source}\n"${story.source_text}"`;
    try { await navigator.clipboard.writeText(text); setCopied(true); showToast('已复制，可粘贴至微信/小红书'); setTimeout(() => setCopied(false), 2000); }
    catch { showToast('复制失败，请手动截图'); }
  };

  return (
    <div className="fixed inset-0 z-[2000] flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm animate-[fadeIn_.2s_ease-out]"
         onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-card border border-border rounded-t-2xl sm:rounded-2xl max-w-sm w-full p-6 space-y-5 animate-[slideUp_.3s_ease-out] shadow-2xl"
           style={{ paddingBottom: 'calc(1.5rem + env(safe-area-inset-bottom, 12px))' }}>
        <div className="flex items-center justify-between">
          <h3 className="font-display font-bold text-fg-primary">分享典故卡片</h3>
          <button onClick={onClose} className="text-fg-tertiary hover:text-fg-secondary">✕</button>
        </div>

        {/* QR Code */}
        <div className="flex flex-col items-center gap-3 p-4 bg-bg rounded-xl">
          {qrUrl ? <img src={qrUrl} alt="QR" className="w-40 h-40 rounded-lg" /> :
            <div className="w-40 h-40 rounded-lg bg-border animate-pulse flex items-center justify-center text-fg-tertiary text-xs">生成中…</div>}
          <p className="text-xs text-fg-tertiary">扫描二维码查看典故详情</p>
        </div>

        <button onClick={handleCopy}
          className={`w-full py-3 rounded-xl font-medium text-sm transition-all ${
            copied ? 'bg-jade/20 text-jade' : 'bg-jade text-black hover:bg-jade-deep'}`}>
          {copied ? '✓ 已复制典故文字' : '复制典故文字'}
        </button>

        <p className="text-[11px] text-fg-tertiary text-center">也可保存卡片图片后分享至微信朋友圈/小红书</p>
      </div>
    </div>
  );
}
