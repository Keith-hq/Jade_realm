import { useCallback, useEffect, useRef, useState } from 'react';

export default function BeforeAfterSlider({ beforeSrc, afterSrc, beforeLabel, afterLabel }) {
  const [pos, setPos] = useState(50);
  const containerRef = useRef(null);
  const dragging = useRef(false);

  const update = useCallback((clientX) => {
    const el = containerRef.current; if (!el) return;
    const rect = el.getBoundingClientRect();
    setPos(Math.max(2, Math.min(98, ((clientX - rect.left) / rect.width) * 100)));
  }, []);

  useEffect(() => {
    const onMove = (e) => { if (!dragging.current) return; e.preventDefault(); update(e.touches?.[0]?.clientX ?? e.clientX); };
    const onUp = () => { dragging.current = false; };
    window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp);
    window.addEventListener('touchmove', onMove, { passive: false }); window.addEventListener('touchend', onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); window.removeEventListener('touchmove', onMove); window.removeEventListener('touchend', onUp); };
  }, [update]);

  return (
    <div ref={containerRef} className="relative w-full aspect-square rounded-2xl overflow-hidden bg-card border border-border select-none">
      {/* After (result) */}
      <img src={afterSrc} alt="" className="absolute inset-0 w-full h-full object-cover" draggable={false} />
      {/* Before (original) clipped */}
      <div className="absolute inset-0 overflow-hidden" style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}>
        <img src={beforeSrc} alt="" className="absolute inset-0 w-full h-full object-cover" draggable={false} />
      </div>
      {/* Divider */}
      <div className="absolute inset-y-0 w-0.5 bg-white shadow-lg z-10" style={{ left: `${pos}%`, transform: 'translateX(-50%)' }}>
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 bg-white rounded-full shadow-xl flex items-center justify-center cursor-ew-resize"
          onMouseDown={() => { dragging.current = true; }} onTouchStart={() => { dragging.current = true; }}
        >
          <svg className="w-5 h-5 text-gray-600" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M3 7a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 6a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" /></svg>
        </div>
      </div>
      {/* Labels */}
      <span className="absolute top-3 left-3 px-2 py-1 bg-black/60 text-white text-xs rounded-lg backdrop-blur-sm z-20 pointer-events-none">{beforeLabel}</span>
      <span className="absolute top-3 right-3 px-2 py-1 bg-black/60 text-jade text-xs rounded-lg backdrop-blur-sm z-20 pointer-events-none">{afterLabel}</span>
    </div>
  );
}
