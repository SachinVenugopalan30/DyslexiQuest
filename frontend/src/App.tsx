import { useState, useEffect } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { IntroScreen } from './components/IntroScreen';
import { GameWindow } from './components/GameWindow';
import { AccessibilityControls } from './components/AccessibilityControls';
import { useGameState } from './hooks/useGameState';
import { setupTooltipPositioning } from './utils/tooltipPositioning';

export interface GameSettings {
  fontSize: 'small' | 'medium' | 'large';
  theme: 'retro' | 'accessible';
  skipAnimations: boolean;
  fontFamily: 'mono' | 'dyslexic' | 'accessible';
}

function App() {
  const [gameSettings, setGameSettings] = useState<GameSettings>({
    fontSize: 'medium',
    theme: 'retro',
    skipAnimations: false,
    fontFamily: 'mono'
  });

  const gameState = useGameState();

  // Setup smart tooltip positioning on component mount
  useEffect(() => {
    setupTooltipPositioning();
  }, []);

  const handleSettingChange = <K extends keyof GameSettings>(
    key: K,
    value: GameSettings[K]
  ) => {
    setGameSettings(prev => ({ ...prev, [key]: value }));
  };

  // Apply theme classes based on settings
  const themeClasses = gameSettings.theme === 'retro' 
    ? 'bg-retro-black text-retro-green' 
    : 'bg-accessible-bg text-accessible-text high-contrast';
    
  const fontClasses = {
    mono: 'font-mono',
    dyslexic: 'font-dyslexic dyslexia-friendly',
    accessible: 'font-accessible dyslexia-friendly'
  }[gameSettings.fontFamily];

  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  }[gameSettings.fontSize];

  return (
    <ErrorBoundary>
      <div 
        className={`min-h-screen ${themeClasses} ${fontClasses} ${sizeClasses} transition-all duration-300`}
        role="main"
  aria-label="DyslexiQuest"
      >
        {!gameState.isGameStarted ? (
          <>
            <AccessibilityControls 
              settings={gameSettings}
              onSettingChange={handleSettingChange}
            />
            <IntroScreen 
              onStartGame={gameState.startGame}
              settings={gameSettings}
            />
          </>
        ) : (
          <GameWindow 
            gameState={gameState}
            settings={gameSettings}
            onSettingChange={handleSettingChange}
          />
        )}
        
        {/* Screen reader announcements */}
        <div 
          id="game-announcements" 
          className="sr-only" 
          aria-live="polite" 
          aria-atomic="true"
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;
