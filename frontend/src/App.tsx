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
  fontFamily: 'poppins' | 'dyslexic';
}

function App() {
  const [gameSettings, setGameSettings] = useState<GameSettings>({
    fontSize: 'medium',
    theme: 'retro',
    skipAnimations: false,
    fontFamily: 'poppins'
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
    ? 'bg-primary-gunmetal text-primary-lavender' 
    : 'bg-accessible-bg text-accessible-text high-contrast';
    
  const fontClasses = {
    poppins: 'font-poppins',
    dyslexic: 'font-dyslexic dyslexia-friendly'
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
            {gameState.isLoading ? (
              // Loading screen when starting a new adventure
              <div className="min-h-screen flex items-center justify-center">
                <div className="text-center max-w-md mx-auto p-8">
                  <div className="mb-8">
                    <div className="loading-spinner w-16 h-16 mx-auto mb-6"></div>
                    <h2 className="text-2xl font-bold text-primary-powder mb-4">
                      🎭 Creating Your Adventure!
                    </h2>
                    <p className="text-primary-lavender leading-relaxed mb-4">
                      Our AI storyteller is crafting a unique adventure just for you...
                    </p>
                    <div className="text-sm text-primary-gray opacity-80">
                      <p>✨ Generating story elements</p>
                      <p>🎯 Setting up challenges</p>
                      <p>📚 Preparing vocabulary words</p>
                    </div>
                  </div>
                  
                  {/* Animated dots to show activity */}
                  <div className="flex justify-center space-x-2 mb-4">
                    <div className="w-2 h-2 bg-primary-green rounded-full animate-pulse delay-0"></div>
                    <div className="w-2 h-2 bg-primary-green rounded-full animate-pulse delay-200"></div>
                    <div className="w-2 h-2 bg-primary-green rounded-full animate-pulse delay-400"></div>
                  </div>
                  
                  <p className="text-xs text-primary-gray opacity-60">
                    This usually takes 3-5 seconds
                  </p>
                </div>
              </div>
            ) : (
              <IntroScreen 
                onStartGame={gameState.startGame}
                settings={gameSettings}
              />
            )}
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
