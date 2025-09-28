import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import { WelcomeScreen } from './components/WelcomeScreen';
import { GameWindow } from './components/GameWindow';
import { AccessibilityControls } from './components/AccessibilityControls';
import { PageTransition } from './components/PageTransition';
import { ThemedLoadingScreen } from './components/ThemedLoadingScreen';
import { useGameState } from './hooks/useGameState';
import { setupTooltipPositioning } from './utils/tooltipPositioning';
import { AdventureTheme, genreMapping } from './types/adventure';
import { saveSelectedAdventure, loadSelectedAdventure, clearSelectedAdventure } from './utils/localStorage';
import { SettingsModal } from './components/SettingsModal';

export interface GameSettings {
  fontSize: 'small' | 'medium' | 'large' | 'x-large';
  theme: 'retro' | 'accessible' | 'modern';
  skipAnimations: boolean;
  fontFamily: 'opendyslexic' | 'poppins';
  backgroundsEnabled: boolean;
  highContrast: boolean;
}

export interface ExtendedGameSettings extends GameSettings {
  selectedAdventure?: AdventureTheme;
}

function App() {
  const [gameSettings, setGameSettings] = useState<GameSettings>({
    fontSize: 'medium',
    theme: 'retro',
    skipAnimations: false,
    fontFamily: 'opendyslexic',
    backgroundsEnabled: true,
    highContrast: false
  });

  const [showGameWindow, setShowGameWindow] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedAdventure, setSelectedAdventure] = useState<AdventureTheme | null>(null);
  const [isTransitioningHome, setIsTransitioningHome] = useState(false);
  const gameState = useGameState();

  // Load selected adventure on mount
  useEffect(() => {
    const savedAdventure = loadSelectedAdventure();
    if (savedAdventure) {
      setSelectedAdventure(savedAdventure);
    }
  }, []);

  // Save selected adventure whenever it changes
  useEffect(() => {
    if (selectedAdventure) {
      saveSelectedAdventure(selectedAdventure);
    }
  }, [selectedAdventure]);

  // Handle smooth transition from loading to game
  useEffect(() => {
    if (gameState.isGameStarted && !gameState.isLoading) {
      const timer = setTimeout(() => {
        setShowGameWindow(true);
      }, 300); // Small delay to ensure smooth transition
      return () => clearTimeout(timer);
    } else if (!gameState.isGameStarted) {
      setShowGameWindow(false);
    }
    return undefined;
  }, [gameState.isGameStarted, gameState.isLoading]);

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

  const handleAdventureSelect = async (adventure: AdventureTheme) => {
    setSelectedAdventure(adventure);
    // Map adventure to backend genre
    const genre = genreMapping[adventure.id];
    await gameState.startGame(genre);
  };

  const handleNewGame = () => {
    setIsTransitioningHome(true);
    setTimeout(() => {
      gameState.newGame();
      setSelectedAdventure(null);
      clearSelectedAdventure();
      setShowGameWindow(false); // Hide game window immediately
      setTimeout(() => {
        setIsTransitioningHome(false);
      }, 400); // Match PageTransition duration
    }, 300); // Fade out duration before switching
  };

  const handleOpenSettings = () => {
    setShowSettings(true);
  };

  const handleCloseSettings = () => {
    setShowSettings(false);
  };

  // Apply theme classes based on settings
  const themeClasses = 
    gameSettings.highContrast 
      ? 'bg-black text-white high-contrast' 
      : gameSettings.theme === 'retro' 
        ? 'bg-primary-gunmetal text-primary-lavender' 
        : gameSettings.theme === 'accessible'
          ? 'bg-accessible-bg text-accessible-text'
          : 'bg-white text-black'; // Modern theme
    
  const fontClasses = {
    opendyslexic: 'font-dyslexic dyslexia-friendly',
    poppins: 'font-poppins'
  }[gameSettings.fontFamily];

  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
    'x-large': 'text-xl'
  }[gameSettings.fontSize];

  return (
    <ErrorBoundary>
      <div 
        className={`min-h-screen ${themeClasses} ${fontClasses} ${sizeClasses} transition-all duration-300`}
        role="main"
        aria-label="DyslexiQuest"
      >
        {/* Home screen (Welcome) with transition */}
        <PageTransition show={!gameState.isGameStarted && !isTransitioningHome} duration={400}>
          <>
            <AccessibilityControls 
              settings={gameSettings}
              onSettingChange={handleSettingChange}
            />
            <WelcomeScreen 
              onAdventureSelect={handleAdventureSelect}
              onOpenSettings={handleOpenSettings}
              settings={gameSettings}
            />
          </>
        </PageTransition>
        {/* Loading screen - only show during initial game start, not during choice selections */}
        <PageTransition show={gameState.isLoading && !gameState.isGameStarted} duration={400}>
          <ThemedLoadingScreen selectedAdventure={selectedAdventure} />
        </PageTransition>
        {/* Game window with transition */}
        <PageTransition show={gameState.isGameStarted && showGameWindow && !isTransitioningHome} duration={600}>
          <GameWindow 
            gameState={gameState}
            settings={gameSettings}
            onSettingChange={handleSettingChange}
            selectedAdventure={selectedAdventure}
            onNewGame={handleNewGame}
          />
        </PageTransition>

        {/* Screen reader announcements */}
        <div 
          id="game-announcements" 
          className="sr-only" 
          aria-live="polite" 
          aria-atomic="true"
        />

      </div>

      {/* Settings Modal - Rendered as Portal */}
      <SettingsModal
        isOpen={showSettings}
        onClose={handleCloseSettings}
        settings={gameSettings}
        onSettingChange={handleSettingChange}
      />
    </ErrorBoundary>
  );
}

export default App;
