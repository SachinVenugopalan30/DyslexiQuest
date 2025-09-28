import { ReactNode } from 'react';
import { AdventureTheme } from '../types/adventure';

interface BackgroundThemeProps {
  adventure: AdventureTheme | null;
  enabled: boolean;
  children: ReactNode;
  className?: string;
}

export const BackgroundTheme: React.FC<BackgroundThemeProps> = ({ 
  adventure, 
  enabled, 
  children, 
  className = '' 
}) => {
  // Generate background classes based on adventure
  const getBackgroundClasses = () => {
    if (!adventure || !enabled) {
      return 'bg-retro-black'; // Default retro theme background
    }

    const adventureClasses = {
      forest: 'game-forest-bg',
      space: 'game-space-bg', 
      magical: 'game-magical-bg',
      mystery: 'game-mystery-bg'
    };

    return adventureClasses[adventure.id] || 'bg-retro-black';
  };

  // Generate overlay classes for text readability
  const getOverlayClasses = () => {
    if (!adventure || !enabled) {
      return '';
    }

    return 'relative before:absolute before:inset-0 before:bg-black before:bg-opacity-20 before:pointer-events-none';
  };

  const backgroundClasses = getBackgroundClasses();
  const overlayClasses = getOverlayClasses();

  return (
    <div 
      className={`${backgroundClasses} ${overlayClasses} ${className}`}
      style={{
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed'
      }}
    >
      {/* Content wrapper with z-index to ensure it's above overlay */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};
