import { useState, useEffect } from 'react';

interface PageTransitionProps {
  children: React.ReactNode;
  show: boolean;
  duration?: number;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({ 
  children, 
  show, 
  duration = 300,
  className = '' 
}) => {
  const [shouldRender, setShouldRender] = useState(show);
  const [isVisible, setIsVisible] = useState(show);

  useEffect(() => {
    if (show) {
      setShouldRender(true);
      // Small delay to ensure DOM is ready before starting animation
      const timer = setTimeout(() => setIsVisible(true), 10);
      return () => clearTimeout(timer);
    } else {
      setIsVisible(false);
      // Wait for animation to complete before unmounting
      const timer = setTimeout(() => setShouldRender(false), duration);
      return () => clearTimeout(timer);
    }
  }, [show, duration]);

  if (!shouldRender) return null;

  return (
    <div 
      className={`page-transition ${isVisible ? 'page-transition-enter' : 'page-transition-exit'} ${className}`}
      style={{ 
        '--transition-duration': `${duration}ms` 
      } as React.CSSProperties}
    >
      {children}
    </div>
  );
};
