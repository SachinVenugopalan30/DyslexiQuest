import { useState } from 'react';
import { AdventureTheme, getAllAdventureThemes } from '../types/adventure';
import { GameSettings } from '../App';
import sunImage from '../assets/sun.png';
import moonImage from '../assets/moon.png';

interface WelcomeScreenProps {
  onAdventureSelect: (adventure: AdventureTheme) => Promise<void>;
  onOpenSettings: () => void;
  settings: GameSettings;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ 
  onAdventureSelect, 
  onOpenSettings,
  settings 
}) => {
  const [selectedAdventure, setSelectedAdventure] = useState<AdventureTheme | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const adventureThemes = getAllAdventureThemes();

  const handleAdventureSelect = async (adventure: AdventureTheme) => {
    if (isLoading) return;
    
    setSelectedAdventure(adventure);
    setIsLoading(true);
    
    try {
      await onAdventureSelect(adventure);
    } catch (error) {
      console.error('Failed to start adventure:', error);
      setSelectedAdventure(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Apply theme classes based on settings
  const themeClasses = 
    settings.theme === 'retro' 
      ? 'bg-primary-gunmetal text-primary-lavender' 
      : settings.theme === 'accessible'
        ? 'bg-accessible-bg text-accessible-text high-contrast'
        : 'bg-white text-black'; // Modern theme

  const fontClasses = {
    poppins: 'font-poppins',
    dyslexic: 'font-dyslexic dyslexia-friendly',
    hyperlegible: 'font-hyperlegible'
  }[settings.fontFamily];

  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base', 
    large: 'text-lg'
  }[settings.fontSize];

  return (
    <div className={`welcome-container ${themeClasses} ${fontClasses} ${sizeClasses}`}>
      <div className="welcome-content">
        {/* Welcome Banner with Sun and Moon */}
        <div className="welcome-banner">
          <img 
            src={sunImage} 
            alt="Sun" 
            className="sun-icon"
          />
          
          <div className="title-container">
            <h1 className="welcome-title">WELCOME</h1>
            <h1 className="welcome-title">DYSLEXIQUEST</h1>
            <h1 className="welcome-title">GAME</h1>
          </div>
          
          <img 
            src={moonImage} 
            alt="Moon" 
            className="moon-icon"
          />
        </div>
        
        {/* Selection Banner */}
        <div className="selection-banner">
          <h2 className="selection-title">CHOOSE YOUR ADVENTURE TYPE :</h2>
        </div>
        
        {/* Adventure Grid */}
        <div className="adventure-grid">
          {adventureThemes.map((adventure) => (
            <div
              key={adventure.id}
              className={`adventure-card ${
                selectedAdventure?.id === adventure.id ? 'selected' : ''
              } ${
                isLoading ? 'disabled' : ''
              }`}
              onClick={() => handleAdventureSelect(adventure)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleAdventureSelect(adventure);
                }
              }}
              aria-label={`Select ${adventure.name} adventure: ${adventure.description}`}
            >
              <div className="adventure-illustration">
                <img 
                  src={adventure.characterImage} 
                  alt={adventure.name}
                  className="adventure-image"
                  loading="lazy"
                />
              </div>
              
              <div className="adventure-content">
                <h3 className="adventure-name">
                  {selectedAdventure?.id === adventure.id && isLoading && '✓ '}
                  {adventure.name}
                </h3>
                <p className="adventure-description">
                  {adventure.description}
                </p>
                
                {isLoading && selectedAdventure?.id === adventure.id && (
                  <div className="loading-indicator">
                    <div className="loading-spinner w-4 h-4"></div>
                    <span className="text-sm">Starting adventure...</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Settings Button */}
        <div className="settings-container">
          <button
            onClick={onOpenSettings}
            className="settings-button"
            aria-label="Open accessibility settings"
          >
            ⚙️ Settings
          </button>
        </div>

        {/* Instructions */}
        <div className="instructions-container">
          <div className="instructions-content">
            <h3 className="instructions-title">📖 HOW TO PLAY:</h3>
            <ul className="instructions-list">
              <li>• Choose an adventure type to begin your story</li>
              <li>• Read each part of the story carefully</li>
              <li>• Choose what you want to do next</li>
              <li>• Click on highlighted words to learn their meanings</li>
              <li>• You can go back to previous choices if needed</li>
              <li>• The game lasts up to 10 turns - make them count!</li>
            </ul>
          </div>
        </div>

        {/* Accessibility Notice */}
        <div className="accessibility-notice">
          <p>
            💡 Use the settings button (⚙️) to adjust 
            text size, colors, and fonts for easier reading.
          </p>
        </div>
      </div>
    </div>
  );
};
