import { useCallback, useRef } from 'react';

export default function WaterRipple({ children, className = '', disabled = false }) {
  const containerRef = useRef(null);

  const createRipple = useCallback((e) => {
    if (disabled) return;
    const container = containerRef.current;
    if (!container) return;
    const rect = container.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 2;
    const x = (e.clientX || (e.touches?.[0]?.clientX ?? rect.left + rect.width / 2)) - rect.left - size / 2;
    const y = (e.clientY || (e.touches?.[0]?.clientY ?? rect.top + rect.height / 2)) - rect.top - size / 2;
    const ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    ripple.style.cssText = `left:${x}px;top:${y}px;width:${size}px;height:${size}px`;
    container.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
  }, [disabled]);

  return (
    <div
      ref={containerRef}
      className={`ripple-container ${className}`}
      onPointerDown={createRipple}
    >
      {children}
    </div>
  );
}
