import { useState, useCallback, useEffect } from 'react';
import { fetchDesignOptions, generateJadeDesign, hasImageKey } from '../../api';
import { showToast } from '../Toast';
import WaterRipple from '../WaterRipple';

const STEPS = { DESIGN: 'design', LOADING: 'loading', RESULT: 'result' };

export default function DynastyFilter() {
  const [step, setStep] = useState(STEPS.DESIGN);
  const [options, setOptions] = useState(null);
  const [selections, setSelections] = useState({});
  const [expanded, setExpanded] = useState('object');
  const [resultUrl, setResultUrl] = useState(null);
  const [resultDynasty, setResultDynasty] = useState('');
  const [error, setError] = useState(null);
  const abortRef = { current: null };

  useEffect(() => {
    fetchDesignOptions().then(setOptions).catch(() => showToast('加载选项失败'));
  }, []);

  const toggleOption = useCallback((catKey, optId, multi) => {
    setSelections(prev => {
      if (multi) {
        const current = prev[catKey] || [];
        const next = current.includes(optId)
          ? current.filter(id => id !== optId)
          : [...current, optId];
        return { ...prev, [catKey]: next };
      }
      return { ...prev, [catKey]: prev[catKey] === optId ? undefined : optId };
    });
    setError(null);
  }, []);

  const selectedCount = useCallback((catKey) => {
    const v = selections[catKey];
    if (!v) return 0;
    return Array.isArray(v) ? v.length : 1;
  }, [selections]);

  const canGenerate = selections.object && selections.material && selections.dynasty;

  const handleGenerate = async () => {
    if (!canGenerate) return;
    if (!hasImageKey()) {
      showToast('请先填写图片 API Key');
      window.dispatchEvent(new Event('jade:open-settings'));
      return;
    }
    setStep(STEPS.LOADING); setError(null);
    const ctrl = new AbortController(); abortRef.current = ctrl;
    try {
      const r = await generateJadeDesign(selections, ctrl.signal);
      setResultUrl(r.result_url);
      setResultDynasty(r.dynasty_label);
      setStep(STEPS.RESULT);
    } catch (e) {
      if (e.name !== 'AbortError') { setError(e.message); setStep(STEPS.DESIGN); }
    } finally { abortRef.current = null; }
  };

  const handleReset = () => {
    abortRef.current?.abort();
    setStep(STEPS.DESIGN); setResultUrl(null); setError(null);
  };

  const getOptById = (catKey, optId) => {
    if (!options) return null;
    return options[catKey]?.options?.find(o => o.id === optId);
  };

  const catOrder = ['object', 'material', 'dynasty', 'visualStyle', 'bgColor', 'pattern', 'craft'];

  return (
    <div className="px-4 py-4 space-y-5 max-w-lg mx-auto">
      {step === STEPS.DESIGN && (
        <>
          <p className="text-xs text-fg-tertiary text-center">
            分级选择，组合你的专属玉器设计
          </p>

          {options && catOrder.map(catKey => {
            const cat = options[catKey];
            if (!cat) return null;
            const isExpanded = expanded === catKey;
            const count = selectedCount(catKey);
            const isMulti = cat.multi;

            return (
              <div key={catKey} className="bg-card border border-border rounded-2xl overflow-hidden">
                {/* Category header */}
                <button
                  onClick={() => setExpanded(isExpanded ? null : catKey)}
                  className={`w-full flex items-center gap-2.5 px-4 py-3 text-left transition-colors ${
                    isExpanded ? 'bg-jade/5' : ''
                  }`}
                >
                  <span className="text-lg">{cat.icon}</span>
                  <span className="font-display font-semibold text-fg-primary text-sm flex-1">
                    {cat.label}
                    {cat.required && <span className="text-seal ml-1">*</span>}
                  </span>
                  {count > 0 && (
                    <span className="px-2 py-0.5 bg-jade/15 text-jade text-[11px] rounded-full font-medium">
                      {isMulti ? `已选 ${count}` : '已选'}
                    </span>
                  )}
                  <svg className={`w-4 h-4 text-fg-tertiary transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                  </svg>
                </button>

                {/* Selected chips (when collapsed) */}
                {!isExpanded && count > 0 && (
                  <div className="px-4 pb-3 flex flex-wrap gap-1.5">
                    {(isMulti
                      ? (selections[catKey] || []).map(id => getOptById(catKey, id))
                      : [getOptById(catKey, selections[catKey])]
                    ).filter(Boolean).map(opt => (
                      <span key={opt.id} className="text-[10px] px-2 py-1 bg-jade/8 text-jade rounded-full">
                        {opt.label}
                      </span>
                    ))}
                  </div>
                )}

                {/* Option grid (when expanded) */}
                {isExpanded && (
                  <div className="px-4 pb-3.5">
                    {cat.desc && <p className="text-[11px] text-fg-tertiary mb-2">{cat.desc}</p>}
                    <div className="flex flex-wrap gap-2">
                      {cat.options.map(opt => {
                        const selected = isMulti
                          ? (selections[catKey] || []).includes(opt.id)
                          : selections[catKey] === opt.id;
                        return (
                          <button
                            key={opt.id}
                            onClick={() => toggleOption(catKey, opt.id, isMulti)}
                            className={`relative flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium transition-all active:scale-95 ${
                              selected
                                ? 'bg-jade text-black shadow-sm'
                                : 'bg-bg text-fg-secondary hover:bg-jade/10 border border-transparent hover:border-jade/30'
                            }`}
                          >
                            {opt.color && (
                              <span className="w-3.5 h-3.5 rounded-full border border-white/30 flex-shrink-0"
                                style={{ backgroundColor: opt.color }} />
                            )}
                            <span>{opt.label}</span>
                            {opt.desc && selected && (
                              <span className="hidden sm:inline text-[10px] opacity-60 ml-0.5">{opt.desc}</span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {error && (
            <div className="text-center bg-seal/10 py-2.5 rounded-lg space-y-2">
              <p className="text-seal text-sm px-3">{error}</p>
              {/key|Key|密钥/i.test(error) && (
                <button onClick={() => window.dispatchEvent(new Event('jade:open-settings'))}
                  className="px-3 py-1.5 bg-seal/20 text-seal text-xs rounded-lg">
                  ⚙️ 去填写 API Key
                </button>
              )}
            </div>
          )}

          {/* Generate CTA */}
          <WaterRipple className="w-full rounded-2xl" disabled={!canGenerate}>
            <button onClick={handleGenerate} disabled={!canGenerate}
              className="w-full py-4 bg-gradient-to-r from-jade via-jade to-jade-deep text-black font-bold text-lg rounded-2xl
                         disabled:opacity-25 disabled:cursor-not-allowed transition-all active:scale-[.98] shadow-lg shadow-jade/20">
              {canGenerate ? '✨ 生成玉器设计' : '请完成必选分类 (*)'}
            </button>
          </WaterRipple>
        </>
      )}

      {step === STEPS.LOADING && (
        <div className="flex flex-col items-center justify-center py-20 gap-6">
          <div className="relative w-20 h-20">
            <svg className="jade-spinner w-full h-full text-jade" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="2" strokeDasharray="8 6" strokeLinecap="round" opacity=".3" />
              <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="2" strokeDasharray="90 120" strokeLinecap="round" strokeDashoffset="30" />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-2xl">💎</span>
          </div>
          <p className="font-display text-fg-secondary text-lg animate-pulse">依汝之选，匠心琢玉…</p>
          <p className="text-fg-tertiary text-sm">AI 正在为你设计专属玉器</p>
        </div>
      )}

      {step === STEPS.RESULT && resultUrl && (
        <div className="space-y-4">
          <div className="relative w-full aspect-square rounded-2xl overflow-hidden bg-card border border-border">
            <img src={resultUrl} alt="" className="absolute inset-0 w-full h-full object-cover" />
            <span className="absolute top-3 right-3 px-2 py-1 bg-black/60 text-jade text-xs rounded-lg backdrop-blur-sm z-20">{resultDynasty}风格玉器</span>
          </div>
          <div className="flex items-center gap-2 justify-center">
            <button onClick={async () => {
              try { const r = await fetch(resultUrl); const b = await r.blob(); const u = URL.createObjectURL(b); const a = document.createElement('a'); a.href = u; a.download = 'jade-design.png'; a.click(); URL.revokeObjectURL(u); showToast('已保存至相册 ✨'); } catch { showToast('保存失败，请重试'); }
            }}
              className="flex items-center gap-2 px-4 py-2.5 bg-jade text-black font-medium rounded-xl text-sm active:scale-95 transition-transform">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              保存图片
            </button>
            <button onClick={() => { navigator.clipboard.writeText(window.location.origin + resultUrl).then(() => showToast('链接已复制，去分享吧')).catch(() => showToast('复制失败')); }}
              className="flex items-center gap-2 px-4 py-2.5 border border-border text-fg-secondary rounded-xl text-sm active:scale-95 transition-transform">
              复制链接
            </button>
            <button onClick={handleReset} className="text-fg-tertiary text-sm underline underline-offset-4">再设计一个</button>
          </div>
        </div>
      )}
    </div>
  );
}
