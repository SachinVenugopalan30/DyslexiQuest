import { useState, useEffect } from 'react';

interface AnimatedChoiceButtonProps {
  choice: string;
  index: number;
  onClick: () => void;
  disabled: boolean;
  delay?: number;
  skipAnimations?: boolean;
}

export const AnimatedChoiceButton: React.FC<AnimatedChoiceButtonProps> = ({
  choice,
  index,
  onClick,
  disabled,
  delay = 0,
  skipAnimations = false
}) => {
  const [isVisible, setIsVisible] = useState(skipAnimations);
  const [hasClicked, setHasClicked] = useState(false);

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

  const handleClick = () => {
    setHasClicked(true);
    // Add a slight delay to show the click animation before processing
    setTimeout(onClick, 150);
  };

  const animationClass = skipAnimations 
    ? '' 
    : isVisible 
      ? 'choice-button-enter' 
      : 'opacity-0 translate-y-4';

  const clickedClass = hasClicked ? 'transform scale-95 bg-retro-green text-retro-black' : '';

  return (
    <button
      onClick={handleClick}
      disabled={disabled || hasClicked}
      className={`
        choice-button p-4 rounded border-2 border-retro-green text-left font-medium text-lg transition-all
        bg-retro-black text-retro-green hover:bg-retro-green hover:text-retro-black
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-retro-amber
        ${animationClass} ${clickedClass}
      `}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'both'
      }}
      aria-label={`Choice ${index + 1}`}
    >
      <div className="flex items-center space-x-3">
        <div className={`
          w-8 h-8 rounded-full flex items-center justify-center font-bold transition-all
          ${hasClicked ? 'bg-retro-black text-retro-green' : 'bg-retro-green text-retro-black'}
        `}>
          {hasClicked ? '✓' : index + 1}
        </div>
        <span className="flex-1">{choice.replace(/^\d+\.\s*/, '')}</span>
      </div>
    </button>
  );
};
