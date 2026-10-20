import { useEffect, useState } from 'react';
import {
  DEFAULT_SETTINGS, checkHealth, clearSettings, loadSettings, saveSettings,
} from '../api';
import { showToast } from './Toast';

export default function SettingsModal({ onClose }) {
  const [form, setForm] = useState(DEFAULT_SETTINGS);
  const [showKeys, setShowKeys] = useState(false);
  const [testing, setTesting] = useState(false);
  const [status, setStatus] = useState(null); // { image: bool, text: bool } | { error }

  useEffect(() => { setForm(loadSettings()); }, []);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSave = () => {
    saveSettings({
      ...form,
      imageKey: form.imageKey.trim(),
      imageModel: form.imageModel.trim() || DEFAULT_SETTINGS.imageModel,
      textKey: form.textKey.trim(),
      textModel: form.textModel.trim() || DEFAULT_SETTINGS.textModel,
      textBase: form.textBase.trim() || DEFAULT_SETTINGS.textBase,
    });
    showToast('设置已保存 ✨');
    onClose();
  };

  const handleTest = async () => {
    setTesting(true); setStatus(null);
    saveSettings(form); // 让后端能看到当前填写的值
    try {
      const h = await checkHealth();
      setStatus({ image: h.has_image_key, text: h.has_text_key });
      if (!h.has_image_key) showToast('后端没收到图片 Key，请检查填写');
    } catch (e) {
      setStatus({ error: e.message });
    } finally {
      setTesting(false);
    }
  };

  const handleClear = () => {
    clearSettings();
    setForm(DEFAULT_SETTINGS);
    setStatus(null);
    showToast('已清除本机保存的 Key');
  };

  const inputCls =
    'w-full px-3 py-2.5 bg-bg border border-border rounded-xl text-sm text-fg-primary placeholder:text-fg-tertiary focus:border-jade/50 transition-colors';

  return (
    <div className="fixed inset-0 z-[2000] flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm"
         onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-card border border-border rounded-t-2xl sm:rounded-2xl max-w-sm w-full max-h-[88vh] overflow-y-auto p-6 space-y-4 shadow-2xl"
           style={{ paddingBottom: 'calc(1.5rem + env(safe-area-inset-bottom, 12px))' }}>

        <div className="flex items-center justify-between">
          <h3 className="font-display font-bold text-fg-primary">模型 API Key</h3>
          <button onClick={onClose} className="text-fg-tertiary hover:text-fg-secondary">✕</button>
        </div>

        <p className="text-[11px] text-fg-tertiary leading-relaxed">
          本项目不内置任何 Key。填入你自己的 Key 即可体验完整生成能力；Key 只保存在本机浏览器，
          仅随请求发给你自己运行的后端。
        </p>

        {/* 图片生成 */}
        <div className="space-y-2 p-3 bg-bg rounded-xl border border-border/60">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-jade">🖼️ 图片生成 · SiliconFlow</span>
            <button onClick={() => setShowKeys((v) => !v)} className="text-[10px] text-fg-tertiary underline underline-offset-2">
              {showKeys ? '隐藏' : '显示'}
            </button>
          </div>
          <input type={showKeys ? 'text' : 'password'} value={form.imageKey} onChange={set('imageKey')}
                 placeholder="sk-...（必填，否则无法生图）" className={inputCls} autoComplete="off" spellCheck={false} />
          <input type="text" value={form.imageModel} onChange={set('imageModel')}
                 placeholder={DEFAULT_SETTINGS.imageModel} className={inputCls} spellCheck={false} />
          <p className="text-[10px] text-fg-tertiary">
            获取 Key：<a className="text-jade underline underline-offset-2" target="_blank" rel="noreferrer"
                        href="https://cloud.siliconflow.cn/account/ak">cloud.siliconflow.cn → API 密钥</a>
          </p>
        </div>

        {/* 文本生成 */}
        <div className="space-y-2 p-3 bg-bg rounded-xl border border-border/60">
          <span className="text-xs font-medium text-gold">📜 文本生成 · OpenAI 兼容（可选）</span>
          <input type={showKeys ? 'text' : 'password'} value={form.textKey} onChange={set('textKey')}
                 placeholder="sk-...（留空则用内置典故模板）" className={inputCls} autoComplete="off" spellCheck={false} />
          <input type="text" value={form.textBase} onChange={set('textBase')}
                 placeholder={DEFAULT_SETTINGS.textBase} className={inputCls} spellCheck={false} />
          <input type="text" value={form.textModel} onChange={set('textModel')}
                 placeholder={DEFAULT_SETTINGS.textModel} className={inputCls} spellCheck={false} />
        </div>

        {status && !status.error && (
          <p className="text-[11px] text-center text-fg-secondary">
            后端识别：图片 Key {status.image ? '✅' : '❌'} · 文本 Key {status.text ? '✅' : '❌'}
          </p>
        )}
        {status?.error && <p className="text-[11px] text-center text-seal">测试失败：{status.error}</p>}

        <div className="flex gap-2">
          <button onClick={handleSave}
                  className="flex-1 py-2.5 bg-jade text-black font-medium rounded-xl text-sm active:scale-95 transition-transform">
            保存
          </button>
          <button onClick={handleTest} disabled={testing}
                  className="px-4 py-2.5 border border-border text-fg-secondary rounded-xl text-sm active:scale-95 transition-transform disabled:opacity-50">
            {testing ? '测试中…' : '测试'}
          </button>
          <button onClick={handleClear}
                  className="px-4 py-2.5 border border-border text-fg-tertiary rounded-xl text-sm active:scale-95 transition-transform">
            清除
          </button>
        </div>

        <p className="text-[10px] text-fg-tertiary text-center">
          也可以把 Key 写进 <span className="text-fg-secondary">backend/.env</span>，全站默认生效
        </p>
      </div>
    </div>
  );
}
