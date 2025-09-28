import { useState, useEffect } from 'react';

interface AnimatedChoiceButtonProps {
  choice: string;
  index: number;
  onClick: () => void;
  disabled: boolean;
  isLoading?: boolean;
  delay?: number;
  skipAnimations?: boolean;
  feedbackState?: 'none' | 'correct' | 'incorrect';
  useThemedStyling?: boolean;
}

export const AnimatedChoiceButton: React.FC<AnimatedChoiceButtonProps> = ({
  choice,
  index,
  onClick,
  disabled,
  isLoading = false,
  delay = 0,
  skipAnimations = false,
  feedbackState = 'none',
  useThemedStyling = false
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
    // Immediately process the click without delay to make it more responsive
    onClick();
  };

  const animationClass = skipAnimations 
    ? '' 
    : isVisible 
      ? 'choice-button-enter' 
      : 'opacity-0 translate-y-4';

  // Enhanced styling logic for themed and feedback states
  const getButtonClasses = () => {
    let baseClasses = 'choice-button p-4 rounded border-2 text-left font-medium text-lg transition-all focus:outline-none focus:ring-2 focus:ring-retro-amber';
    
    // Add loading/disabled styling
    if (disabled && hasClicked) {
      baseClasses += ' opacity-70 cursor-wait pointer-events-none';
    } else if (disabled) {
      baseClasses += ' opacity-50 cursor-not-allowed';
    }
    
    // Apply feedback state styling
    if (feedbackState === 'correct') {
      return `${baseClasses} choice-button-correct ${animationClass}`;
    }
    
    if (feedbackState === 'incorrect') {
      return `${baseClasses} choice-button-incorrect ${animationClass}`;
    }
    
    // Apply themed styling if enabled
    if (useThemedStyling) {
      const clickedThemedClass = hasClicked && disabled ? 'transform scale-95 bg-opacity-60 animate-pulse' : hasClicked ? 'transform scale-95 bg-opacity-80' : '';
      return `${baseClasses} choice-button-themed hover:transform hover:translateY(-2px) ${animationClass} ${clickedThemedClass}`;
    }
    
    // Default retro styling
    const clickedClass = hasClicked && disabled ? 'transform scale-95 bg-retro-green text-retro-black animate-pulse' : hasClicked ? 'transform scale-95 bg-retro-green text-retro-black' : '';
    return `${baseClasses} border-retro-green bg-retro-black text-retro-green hover:bg-retro-green hover:text-retro-black ${animationClass} ${clickedClass}`;
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || hasClicked || feedbackState !== 'none'}
      className={getButtonClasses()}
      style={{
        animationDelay: `${delay}ms`,
        animationFillMode: 'both'
      }}
      aria-label={`Choice ${index + 1}`}
    >
      <div className="flex items-center space-x-3">
        <div className={`
          w-8 h-8 rounded-full flex items-center justify-center font-bold transition-all
          ${feedbackState === 'correct' 
            ? 'bg-green-600 text-white' 
            : feedbackState === 'incorrect'
              ? 'bg-red-600 text-white'
              : hasClicked && useThemedStyling
                ? 'bg-white bg-opacity-20 text-current'
                : hasClicked
                  ? 'bg-retro-black text-retro-green'
                  : useThemedStyling
                    ? 'bg-black bg-opacity-20 text-current'
                    : 'bg-retro-green text-retro-black'
          }
        `}>
          {feedbackState === 'correct' 
            ? '✓' 
            : feedbackState === 'incorrect'
              ? '✕'
              : hasClicked 
                ? '✓' 
                : index + 1
          }
        </div>
        <span className="flex-1">{choice.replace(/^\d+\.\s*/, '')}</span>
        {isLoading && (
          <div className="loading-spinner w-4 h-4" />
        )}
        {feedbackState !== 'none' && (
          <div className="answer-indicator">
            <span className="text-lg font-bold">
              {feedbackState === 'correct' ? '✓' : '✕'}
            </span>
          </div>
        )}
      </div>
    </button>
  );
};
