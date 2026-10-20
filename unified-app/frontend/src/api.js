const BASE = '/api';

// ─────────────────────────────────────────────
// 用户自带 Key：只存在浏览器 localStorage，随请求头发给本地后端
// ─────────────────────────────────────────────
const SETTINGS_KEY = 'jade.settings.v1';

export const DEFAULT_SETTINGS = {
  imageKey: '',
  imageModel: 'Tongyi-MAI/Z-Image-Turbo',
  textKey: '',
  textModel: 'gpt-4o-mini',
  textBase: 'https://api.openai.com/v1',
};

export function loadSettings() {
  try {
    return { ...DEFAULT_SETTINGS, ...(JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}') || {}) };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

export function saveSettings(next) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(next));
  window.dispatchEvent(new Event('jade:settings'));
}

export function clearSettings() {
  localStorage.removeItem(SETTINGS_KEY);
  window.dispatchEvent(new Event('jade:settings'));
}

export function hasImageKey() {
  return !!loadSettings().imageKey.trim();
}

function authHeaders(extra = {}) {
  const s = loadSettings();
  const h = { ...extra };
  if (s.imageKey) h['X-Image-Key'] = s.imageKey;
  if (s.imageModel) h['X-Image-Model'] = s.imageModel;
  if (s.textKey) h['X-Text-Key'] = s.textKey;
  if (s.textModel) h['X-Text-Model'] = s.textModel;
  if (s.textBase) h['X-Text-Base'] = s.textBase;
  return h;
}

async function asError(r, fallback) {
  const d = await r.json().catch(() => ({}));
  return new Error(d.detail || `${fallback} (${r.status})`);
}

export async function fetchDynasties() {
  const r = await fetch(`${BASE}/dynasties`);
  if (!r.ok) throw new Error('Failed to load dynasties');
  return r.json();
}

export async function fetchDesignOptions() {
  const r = await fetch(`${BASE}/design-options`);
  if (!r.ok) throw new Error('Failed to load design options');
  return r.json();
}

export async function generateJadeDesign(selections, signal) {
  const r = await fetch(`${BASE}/generate-jade-design`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(selections),
    signal,
  });
  if (!r.ok) throw await asError(r, 'Generation failed');
  return r.json();
}

export async function fetchPresets() {
  const r = await fetch(`${BASE}/presets`);
  if (!r.ok) throw new Error('Failed to load presets');
  return r.json();
}

export async function generateStory(keyword, signal) {
  const r = await fetch(`${BASE}/generate-story`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ keyword }),
    signal,
  });
  if (!r.ok) throw await asError(r, 'Generation failed');
  return r.json();
}

/** Ask the backend what credentials it can see — proves the headers arrive. */
export async function checkHealth() {
  const r = await fetch(`${BASE}/health`, { headers: authHeaders() });
  if (!r.ok) throw new Error(`Backend unreachable (${r.status})`);
  return r.json();
}
