import { useState, useEffect } from 'react';

interface AnimatedComponentProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
  skipAnimations?: boolean;
}

export const AnimatedComponent: React.FC<AnimatedComponentProps> = ({ 
  children, 
  delay = 0, 
  duration = 600,
  className = '',
  skipAnimations = false 
}) => {
  const [isVisible, setIsVisible] = useState(skipAnimations);

  useEffect(() => {
    if (skipAnimations) {
      setIsVisible(true);
      return;
    }

    const timer = setTimeout(() => {
      setIsVisible(true);
    }, delay);

    return () => clearTimeout(timer);
  }, [delay, skipAnimations]);

  if (skipAnimations) {
    return <div className={className}>{children}</div>;
  }

  return (
    <div 
      className={`
        ${isVisible 
          ? 'opacity-100 transform translate-y-0' 
          : 'opacity-0 transform translate-y-4'
        }
        transition-all ease-out
        ${className}
      `}
      style={{
        transitionDuration: `${duration}ms`,
        transitionDelay: skipAnimations ? '0ms' : `${delay}ms`
      }}
    >
      {children}
    </div>
  );
};
