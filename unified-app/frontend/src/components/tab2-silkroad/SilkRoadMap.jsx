import { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import { ROUTE_COLORS, ROUTES, MARKERS, MARKER_ORDER, TIMELINE_EVENTS, DEFAULT_CENTER, DEFAULT_ZOOM } from './mapData';

export default function SilkRoadMap() {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const routeLayers = useRef({});
  const markerGroups = useRef({});
  const eventLayer = useRef(null);
  const [activeRoute, setActiveRoute] = useState('hotan');
  const [selectedNode, setSelectedNode] = useState(null);
  const [currentYear, setCurrentYear] = useState(-2000);
  const [playing, setPlaying] = useState(false);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const audioRef = useRef(null);
  const playInterval = useRef(null);

  // Init map — ResizeObserver ensures correct sizing after layout
  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    let resizeObserver;
    let initTimeout;

    const createMap = () => {
      const container = mapRef.current;
      if (!container || mapInstance.current) return;
      // Force container to have explicit dimensions before Leaflet init
      if (container.clientHeight === 0) return false;

      const map = L.map(container, {
        center: DEFAULT_CENTER, zoom: DEFAULT_ZOOM, minZoom: 2, maxZoom: 10,
        zoomControl: false, attributionControl: false, scrollWheelZoom: true, dragging: true, tap: true,
      });
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a>', subdomains: 'abcd', maxZoom: 19,
      }).addTo(map);
      L.control.zoom({ position: 'bottomright' }).addTo(map);

      // Draw all routes
      Object.values(ROUTES).forEach(r => {
        const poly = L.polyline(r.path, {
          color: r.color.line, weight: 3, opacity: .8, dashArray: '10, 8', lineCap: 'round',
        }).addTo(map);
        routeLayers.current[r.id] = poly;

        // Markers
        const mg = L.layerGroup().addTo(map);
        markerGroups.current[r.id] = mg;
        (MARKER_ORDER[r.id] || []).forEach(mid => {
          const m = MARKERS[mid]; if (!m) return;
          const isEndpoint = r.path[0] === m.latlng || r.path[r.path.length - 1] === m.latlng;
          const cm = L.circleMarker(m.latlng, {
            radius: isEndpoint ? 8 : 6, fillColor: r.color.line, color: '#fff', weight: 2, fillOpacity: .9,
          }).addTo(mg);
          cm.bindPopup(`
            <div style="font-family:'Noto Sans SC',sans-serif;min-width:220px">
              <h4 style="font-family:'Noto Serif SC',serif;font-size:15px;font-weight:700;color:#f5f5f4;margin:0 0 2px">${m.name}</h4>
              <p style="font-size:10px;color:#a8a29e;margin:0 0 8px">${m.nameEn}</p>
              <p style="font-size:11px;color:#a8a29e;line-height:1.5;margin:0 0 6px">${m.desc}</p>
              <p style="font-size:10px;color:#4ade80;margin:0">${m.artifact} · ${m.material}</p>
              <p style="font-size:10px;color:#57534e;margin:4px 0 0">${m.period}</p>
            </div>
          `, { maxWidth: 280, className: 'dark-popup' });
          cm.on('click', () => setSelectedNode(m));
        });
      });

      // Event layer
      eventLayer.current = L.layerGroup().addTo(map);
      mapInstance.current = map;
      return true;
    };

    // Try to init with retries, waiting for container to have real dimensions
    const tryInit = (attempts = 0) => {
      if (mapInstance.current) return;
      if (createMap()) return;
      if (attempts < 6) {
        initTimeout = setTimeout(() => tryInit(attempts + 1), 80);
      }
    };

    // Use ResizeObserver to detect when container gets real size
    resizeObserver = new ResizeObserver(() => {
      if (!mapInstance.current && mapRef.current?.clientHeight > 0) {
        createMap();
      }
      // Keep map size in sync with container
      if (mapInstance.current) {
        mapInstance.current.invalidateSize();
      }
    });
    resizeObserver.observe(mapRef.current);

    // Fallback: try init after a short delay anyway
    initTimeout = setTimeout(() => tryInit(), 100);

    return () => {
      resizeObserver?.disconnect();
      clearTimeout(initTimeout);
      if (mapInstance.current) { mapInstance.current.remove(); mapInstance.current = null; }
    };
  }, []);

  // Route visibility toggle
  useEffect(() => {
    if (!mapInstance.current) return;
    Object.entries(routeLayers.current).forEach(([id, layer]) => {
      id === activeRoute ? layer.setStyle({ weight: 4, opacity: 1, dashArray: '12, 6' }) : layer.setStyle({ weight: 2, opacity: .35, dashArray: '8, 10' });
    });
    // Fit bounds to active route
    const r = ROUTES[activeRoute];
    if (r?.path.length) {
      mapInstance.current.flyToBounds(L.latLngBounds(r.path), { padding: [40, 40], maxZoom: 6, duration: 1 });
    }
  }, [activeRoute]);

  // Timeline filtering
  useEffect(() => {
    if (!mapInstance.current || !eventLayer.current) return;
    eventLayer.current.clearLayers();
    TIMELINE_EVENTS.forEach(evt => {
      if (evt.year <= currentYear && currentYear - evt.year <= 500) {
        const m = L.marker(evt.latlng, {
          icon: L.divIcon({ className: '', html: `<div class="event-dot active" style="background:${ROUTE_COLORS[evt.routeId]?.line||'#4ade80'}"></div>`, iconSize: [12,12], iconAnchor: [6,6] }),
        }).addTo(eventLayer.current);
        m.bindPopup(`<div style="font-family:'Noto Sans SC',sans-serif"><b style="color:#f5f5f4">${evt.icon} ${evt.title}</b><br><span style="font-size:10px;color:#a8a29e">${evt.label}</span><br><p style="font-size:11px;color:#a8a29e;margin-top:4px">${evt.summary}</p></div>`, { maxWidth: 260 });
      }
    });
  }, [currentYear]);

  // Play timeline
  useEffect(() => {
    if (playing) {
      playInterval.current = setInterval(() => {
        setCurrentYear(y => { if (y >= 1800) { setPlaying(false); return 1800; } return y + 100; });
      }, 300);
    } else { if (playInterval.current) clearInterval(playInterval.current); }
    return () => { if (playInterval.current) clearInterval(playInterval.current); };
  }, [playing]);

  const toggleAudio = useCallback((url) => {
    if (!url) return;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; setAudioPlaying(false); }
    if (!audioPlaying) {
      const a = new Audio(url); a.play().catch(() => {}); a.onended = () => setAudioPlaying(false);
      audioRef.current = a; setAudioPlaying(true);
    }
  }, [audioPlaying]);

  const yearLabel = currentYear < 0 ? `公元前 ${Math.abs(currentYear)} 年` : currentYear === 0 ? '公元元年' : `公元 ${currentYear} 年`;

  return (
    <div className="flex flex-col h-full">
      {/* Route switcher */}
      <div className="flex gap-1 px-3 py-2 overflow-x-auto no-scrollbar">
        {Object.entries(ROUTE_COLORS).map(([id, c]) => (
          <button key={id} onClick={() => setActiveRoute(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex-shrink-0
              ${activeRoute === id ? 'text-black font-semibold shadow-md' : 'bg-card border border-border text-fg-secondary'}`}
            style={activeRoute === id ? { background: c.line } : {}}
          >
            <span className="w-2 h-2 rounded-full" style={{ background: c.line }} />{c.name}
          </button>
        ))}
      </div>

      {/* Map */}
      <div ref={mapRef} className="flex-1 w-full" />

      {/* Timeline */}
      <div className="px-3 py-2 bg-card border-t border-border space-y-1">
        <div className="flex items-center justify-between">
          <span className="font-display text-sm font-bold text-fg-primary">{yearLabel}</span>
          <div className="flex items-center gap-2">
            <button onClick={() => setCurrentYear(y => Math.max(-2000, y - 200))} className="w-7 h-7 rounded-full bg-bg border border-border text-fg-secondary text-xs flex items-center justify-center">◀</button>
            <button onClick={() => setPlaying(!playing)} className="w-9 h-9 rounded-full flex items-center justify-center text-sm" style={{ background: playing ? '#dc2626' : '#4ade80' }}>
              {playing ? '⏸' : '▶'}
            </button>
            <button onClick={() => setCurrentYear(y => Math.min(1800, y + 200))} className="w-7 h-7 rounded-full bg-bg border border-border text-fg-secondary text-xs flex items-center justify-center">▶</button>
          </div>
        </div>
        <input type="range" min={-2000} max={1800} step={50} value={currentYear}
          onChange={(e) => setCurrentYear(parseInt(e.target.value))}
          className="w-full" style={{ background: `linear-gradient(90deg, #4ade80 ${(currentYear+2000)/3800*45}%, #fbbf24 ${(currentYear+2000)/3800*55}%, #60a5fa)` }} />
        <div className="flex justify-between text-[10px] text-fg-tertiary">
          <span>公元前2000年</span><span>公元元年</span><span>公元1800年</span>
        </div>
      </div>

      {/* Event timeline list */}
      <div className="px-3 pb-1 flex gap-2 overflow-x-auto no-scrollbar">
        {TIMELINE_EVENTS.filter(e => e.year <= currentYear).slice(-8).map((e, i) => (
          <button key={i} onClick={() => { setCurrentYear(e.year); mapInstance.current?.flyTo(e.latlng, 6, { duration: 1 }); }}
            className="flex-shrink-0 bg-card border border-border rounded-lg p-2 text-left max-w-[200px] hover:border-jade/30 transition-colors">
            <span className="text-sm">{e.icon}</span>
            <p className="text-[10px] text-fg-secondary font-medium mt-1 line-clamp-1">{e.title}</p>
            <p className="text-[9px] text-fg-tertiary">{e.label}</p>
          </button>
        ))}
      </div>

      {/* Node detail bottom sheet */}
      {selectedNode && (
        <div className="fixed inset-x-0 bottom-14 z-[900] bg-card/98 backdrop-blur-xl border-t border-border rounded-t-2xl shadow-2xl max-h-[45vh] overflow-y-auto animate-[slideUp_.3s_ease-out]" style={{ paddingBottom: 'env(safe-area-inset-bottom, 12px)' }}>
          <div className="sticky top-0 flex items-center justify-between px-4 py-3 bg-card/95 backdrop-blur-sm border-b border-border">
            <h3 className="font-display font-bold text-fg-primary">{selectedNode.name} <span className="text-xs text-fg-tertiary font-normal">{selectedNode.nameEn}</span></h3>
            <button onClick={() => { setSelectedNode(null); setAudioPlaying(false); if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; } }}
              className="w-7 h-7 rounded-full bg-bg border border-border text-fg-secondary flex items-center justify-center">✕</button>
          </div>
          <div className="p-4 space-y-3">
            <p className="text-sm text-fg-secondary leading-relaxed">{selectedNode.desc}</p>
            <div className="flex items-center gap-3 p-3 bg-bg rounded-xl">
              <div className="w-12 h-12 rounded-lg bg-jade/10 flex items-center justify-center text-xl flex-shrink-0">💎</div>
              <div>
                <p className="text-sm font-medium text-fg-primary">{selectedNode.artifact}</p>
                <p className="text-xs text-fg-tertiary">{selectedNode.material} · {selectedNode.period}</p>
              </div>
            </div>
            {selectedNode.audio && (
              <button onClick={() => toggleAudio(selectedNode.audio)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium w-full justify-center transition-all ${
                  audioPlaying ? 'bg-jade/20 text-jade' : 'bg-bg border border-border text-fg-secondary'}`}>
                {audioPlaying ? '⏸ 暂停讲解' : '▶ 聆听讲解 (30秒)'}
              </button>
            )}
            <p className="text-[11px] text-fg-tertiary text-center">上滑查看知识拓展 →</p>
          </div>
        </div>
      )}
      {selectedNode && <div className="fixed inset-0 z-[899] bg-black/40" onClick={() => setSelectedNode(null)} />}
    </div>
  );
}
