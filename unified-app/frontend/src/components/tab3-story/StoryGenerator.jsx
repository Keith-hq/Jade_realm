import { useState, useRef, useEffect, useCallback } from 'react';
import { fetchPresets, generateStory, hasImageKey } from '../../api';
import { showToast } from '../Toast';
import WaterRipple from '../WaterRipple';
import ShareModal from './ShareModal';
import { toPng } from 'html-to-image';

const FALLBACK_PRESETS = [
  { keyword:'君子佩玉',explanation:'君子以玉比德，佩玉自省。' },
  { keyword:'弄玉吹箫',explanation:'弄玉吹箫引凤，乘凤飞升。' },
  { keyword:'完璧归赵',explanation:'蔺相如智勇护璧，完璧归赵。' },
  { keyword:'化干戈为玉帛',explanation:'化战争为和平，玉帛为礼。' },
  { keyword:'金玉满堂',explanation:'财富无常，德行长久。' },
  { keyword:'冰清玉洁',explanation:'品格高洁如冰玉无瑕。' },
];

const STEPS = { INPUT:'input', LOADING:'loading', RESULT:'result' };

export default function StoryGenerator() {
  const [step, setStep] = useState(STEPS.INPUT);
  const [keyword, setKeyword] = useState('');
  const [presets, setPresets] = useState(FALLBACK_PRESETS);
  const [story, setStory] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);
  const [qrUrl, setQrUrl] = useState(null);
  const [keyReady, setKeyReady] = useState(() => hasImageKey());
  const cardRef = useRef(null);
  const abortRef = useRef(null);

  useEffect(() => { fetchPresets().then(d => { if (d?.length) setPresets(d); }).catch(() => {}); }, []);
  useEffect(() => {
    const sync = () => setKeyReady(hasImageKey());
    window.addEventListener('jade:settings', sync);
    return () => window.removeEventListener('jade:settings', sync);
  }, []);

  const doGenerate = useCallback(async (kw) => {
    setStep(STEPS.LOADING); setError(null); setStory(null);
    const ctrl = new AbortController(); abortRef.current = ctrl;
    try {
      const r = await generateStory(kw, ctrl.signal);
      setStory(r); setStep(STEPS.RESULT);
      // Pre-generate QR code
      import('qrcode').then(QR => {
        QR.toDataURL(`【玉文化典故】${r.title}\n${r.explanation}\n——${r.source}`, { width:200, margin:2, color:{dark:'#f5f5f4',light:'#1a1a1a'} },
          (err, url) => { if (!err) setQrUrl(url); });
      }).catch(() => {});
    } catch (e) { if (e.name !== 'AbortError') { setError(e.message); setStep(STEPS.INPUT); } }
    finally { abortRef.current = null; }
  }, []);

  const handleSave = async () => {
    if (!cardRef.current || saving) return; setSaving(true);
    try {
      const dataUrl = await toPng(cardRef.current, { quality:.95, pixelRatio:2 });
      const a = document.createElement('a'); a.href = dataUrl; a.download = `jade-story-${story?.title||'card'}.png`;
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      showToast('典故卡片已保存 ✨');
    } catch { showToast('保存失败，请重试'); }
    finally { setSaving(false); }
  };

  const handleReset = () => { abortRef.current?.abort(); setStep(STEPS.INPUT); setStory(null); setError(null); setQrUrl(null); };

  return (
    <div className="px-4 py-4 space-y-5 max-w-lg mx-auto">
      {step === STEPS.INPUT && (
        <>
          {/* Search */}
          <form onSubmit={(e) => { e.preventDefault(); const kw = keyword.trim(); if (kw) doGenerate(kw); }} className="flex gap-2">
            <input value={keyword} onChange={e => setKeyword(e.target.value)} placeholder="输入典故关键词…" maxLength={30}
              className="flex-1 px-4 py-3 bg-card border border-border rounded-xl text-fg-primary placeholder:text-fg-tertiary text-sm focus:border-jade/50 transition-colors" />
            <button type="submit" disabled={!keyword.trim()}
              className="px-5 py-3 bg-jade text-black font-medium rounded-xl disabled:opacity-25 transition-all text-sm">搜索</button>
          </form>

          {/* Presets */}
          <div>
            <h3 className="text-xs text-fg-tertiary mb-2.5 font-medium">热门典故 · 一键生成</h3>
            <div className="grid grid-cols-3 gap-2">
              {presets.map(p => (
                <button key={p.keyword} onClick={() => doGenerate(p.keyword)}
                  className="p-3 bg-card border border-border rounded-xl text-center hover:border-jade/40 active:scale-[.97] transition-all">
                  <p className="font-display font-bold text-fg-primary text-sm">{p.keyword}</p>
                  <p className="text-[10px] text-fg-tertiary mt-1 line-clamp-1">{p.explanation}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Random */}
          <WaterRipple className="w-full rounded-xl">
            <button onClick={() => { const kw = presets[Math.floor(Math.random()*presets.length)]?.keyword || '君子佩玉'; setKeyword(kw); doGenerate(kw); }}
              className="w-full py-3 border border-gold/40 text-gold font-medium rounded-xl text-sm active:scale-[.98] transition-all">
              🎲 随机探索一个典故
            </button>
          </WaterRipple>

          {!keyReady && (
            <button onClick={() => window.dispatchEvent(new Event('jade:open-settings'))}
              className="w-full px-3 py-2 rounded-xl bg-gold/10 border border-gold/25 text-[11px] text-gold text-left leading-relaxed">
              🔑 未配置图片 Key — 典故文字照常生成，卡片暂不含 AI 配图。点击填写 →
            </button>
          )}

          {error && <p className="text-seal text-sm text-center bg-seal/10 py-2 rounded-lg">{error}</p>}
        </>
      )}

      {step === STEPS.LOADING && (
        <div className="flex flex-col items-center justify-center py-20 gap-6">
          <div className="relative w-20 h-20">
            <svg className="jade-spinner w-full h-full text-jade" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="2" strokeDasharray="8 6" strokeLinecap="round" opacity=".3" />
              <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="2" strokeDasharray="90 120" strokeLinecap="round" strokeDashoffset="30" />
            </svg>
          </div>
          <p className="font-display text-fg-secondary text-lg animate-pulse">研墨写典，丹青绘玉…</p>
          <p className="text-fg-tertiary text-sm">AI 正在翻阅千年典籍</p>
        </div>
      )}

      {step === STEPS.RESULT && story && (
        <div className="space-y-4">
          {/* Card */}
          <div ref={cardRef} className="card-capture">
            <div className="card-inner">
              {/* Illustration */}
              <div className="h-56 overflow-hidden bg-bg">
                {story.illustration_url ? (
                  <img src={story.illustration_url} alt="" className="w-full h-full object-cover" crossOrigin="anonymous" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-6xl font-calligraphy text-fg-tertiary">玉</div>
                )}
              </div>
              {/* Content */}
              <div className="px-6 pt-5 pb-2 text-center">
                <h2 className="font-display text-2xl font-bold text-fg-primary">{story.title}</h2>
                <p className="text-xs text-fg-tertiary mt-1">{story.title_en}</p>
              </div>
              <div className="flex items-center gap-2 px-6 pb-4"><span className="flex-1 h-px bg-border" /><span className="w-2 h-2 rounded-full bg-jade/60" /><span className="flex-1 h-px bg-border" /></div>
              <div className="px-6 pb-5 text-center"><p className="font-display text-sm leading-relaxed text-fg-secondary">{story.explanation}</p></div>
              <div className="px-6 pb-5 text-center space-y-2">
                <span className="inline-block px-3 py-1 border border-seal/40 text-seal text-xs font-calligraphy rounded rotate-[-2deg]">{story.source}</span>
                <p className="font-display text-sm text-fg-tertiary italic">"{story.source_text}"</p>
              </div>
              <div className="h-1 bg-gradient-to-r from-jade/20 via-jade/50 to-jade/20" />
            </div>
          </div>

          {/* Knowledge extension */}
          <div className="bg-card border border-border rounded-xl p-4 space-y-2">
            <h4 className="text-xs font-medium text-gold">📖 知识拓展</h4>
            <p className="text-sm text-fg-secondary">
              这是"<span className="text-jade font-medium">{story.title}</span>"典故在<span className="text-gold font-medium">{story.source}</span>中的记载。
            </p>
            <div className="flex flex-wrap gap-2 text-xs">
              <a href={`https://so.gushiwen.cn/search.aspx?value=${encodeURIComponent(story.source)}`} target="_blank" rel="noopener"
                className="px-3 py-1.5 bg-bg border border-border rounded-lg text-fg-secondary hover:border-jade/40 transition-colors">
                查看《{story.source.replace(/[《》]/g,'')}》全文 →
              </a>
              <button onClick={() => { setKeyword(story.keyword); doGenerate(story.keyword); }}
                className="px-3 py-1.5 bg-bg border border-border rounded-lg text-fg-secondary hover:border-jade/40 transition-colors">
                相关典故：玉有五德
              </button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 justify-center flex-wrap">
            <button onClick={handleSave} disabled={saving}
              className="flex items-center gap-2 px-5 py-2.5 bg-jade text-black font-medium rounded-xl text-sm active:scale-95 transition-transform disabled:opacity-50">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              {saving ? '保存中…' : '保存图片'}
            </button>
            <button onClick={() => setShareOpen(true)}
              className="flex items-center gap-2 px-5 py-2.5 border border-border text-fg-secondary rounded-xl text-sm active:scale-95 transition-transform">
              分享卡片
            </button>
            <button onClick={handleReset} className="text-fg-tertiary text-sm underline underline-offset-4">换一个典故</button>
          </div>
        </div>
      )}

      {shareOpen && <ShareModal story={story} qrUrl={qrUrl} onClose={() => setShareOpen(false)} />}
    </div>
  );
}
