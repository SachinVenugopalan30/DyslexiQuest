import { useState, useEffect, useRef } from 'react';
import { GameSettings } from '../App';
import { UseGameStateReturn } from '../hooks/useGameState';
import { BreadcrumbTrail } from './BreadcrumbTrail';
import { VocabularyTracker } from './VocabularyTracker';
import { AccessibilityControls } from './AccessibilityControls';
import { highlightVocabularyWords } from '../utils/vocabulary';

interface GameWindowProps {
  gameState: UseGameStateReturn;
  settings: GameSettings;
  onSettingChange: <K extends keyof GameSettings>(key: K, value: GameSettings[K]) => void;
}

export const GameWindow: React.FC<GameWindowProps> = ({ gameState, settings, onSettingChange }) => {
  const [isTyping, setIsTyping] = useState(false);
  const [displayedText, setDisplayedText] = useState('');
  const outputRef = useRef<HTMLDivElement>(null);
  const endOfContentRef = useRef<HTMLDivElement>(null);

  const currentTurn = gameState.gameState?.history[gameState.gameState.history.length - 1];

  // Auto-scroll disabled for better reading experience with dyslexic children
  // Children need to read at their own pace without distracting movement
  // useEffect(() => {
  //   if (endOfContentRef.current && !isTyping) {
  //     endOfContentRef.current.scrollIntoView({ behavior: 'smooth' });
  //   }
  // }, [gameState.gameState?.history, isTyping]);

  // Typewriter effect for AI responses
  useEffect(() => {
    if (!currentTurn || settings.skipAnimations) {
      setDisplayedText(currentTurn?.ai_response || '');
      return;
    }

    setIsTyping(true);
    setDisplayedText('');
    
    const text = currentTurn.ai_response;
    let index = 0;
    
    const typeInterval = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.substring(0, index + 1));
        index++;
      } else {
        clearInterval(typeInterval);
        setIsTyping(false);
      }
    }, 15); // Typing speed - faster animation (was 30ms, now 15ms)

    return () => {
      clearInterval(typeInterval);
      setIsTyping(false);
    };
  }, [currentTurn?.ai_response, settings.skipAnimations]);

  // Tooltip positioning fix
  useEffect(() => {
    const eventListeners = new Map<Element, (event: Event) => void>();

    const positionTooltips = () => {
      const words = document.querySelectorAll('.vocabulary-word');
      
      words.forEach((word) => {
        const tooltip = word.querySelector('.vocabulary-tooltip') as HTMLElement;
        if (!tooltip) return;

        // Remove existing event listener if any
        if (eventListeners.has(word)) {
          word.removeEventListener('mouseenter', eventListeners.get(word)!);
        }

        // Create new event listener
        const mouseEnterHandler = () => {
          const wordRect = word.getBoundingClientRect();
          const tooltipRect = tooltip.getBoundingClientRect();
          
          // Position tooltip above the word
          tooltip.style.position = 'fixed';
          tooltip.style.left = Math.max(10, Math.min(
            wordRect.left + wordRect.width / 2 - tooltipRect.width / 2,
            window.innerWidth - tooltipRect.width - 10
          )) + 'px';
          tooltip.style.top = (wordRect.top - tooltipRect.height - 12) + 'px';
        };

        // Add new event listener
        word.addEventListener('mouseenter', mouseEnterHandler);
        eventListeners.set(word, mouseEnterHandler);
      });
    };

    // Run after content updates
    const timer = setTimeout(positionTooltips, 100);
    
    // Cleanup function
    return () => {
      clearTimeout(timer);
      // Remove all event listeners
      eventListeners.forEach((handler, element) => {
        element.removeEventListener('mouseenter', handler);
      });
      eventListeners.clear();
    };
  }, [displayedText, gameState.gameState?.history]);

  const handleSkipAnimation = () => {
    if (currentTurn) {
      setDisplayedText(currentTurn.ai_response);
      setIsTyping(false);
    }
  };

  if (!gameState.gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p>Loading your adventure...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header with game info */}
      <header className="border-b border-retro-green p-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
          <div>
            <h1 className="text-xl font-bold text-retro-amber">
              {gameState.gameState.genre.charAt(0).toUpperCase() + gameState.gameState.genre.slice(1)} Adventure
            </h1>
            <p className="text-sm">
              Turn {gameState.gameState.turn} of 15
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Progress bar */}
            <div className="progress-bar w-24 h-2 hidden sm:block">
              <div 
                className="progress-bar-fill"
                style={{ width: `${(gameState.gameState.turn / 15) * 100}%` }}
                role="progressbar"
                aria-valuenow={gameState.gameState.turn}
                aria-valuemin={0}
                aria-valuemax={15}
                aria-label={`Game progress: ${gameState.gameState.turn} of 15 turns`}
              />
            </div>
            
            {/* New Game button */}
            <button
              onClick={gameState.newGame}
              className="btn-secondary text-sm px-3 py-1 whitespace-nowrap"
              aria-label="Start a new adventure"
            >
              NEW GAME
            </button>

            {/* Accessibility Controls - inline version */}
            <AccessibilityControls 
              settings={settings}
              onSettingChange={onSettingChange}
              inline={true}
            />
          </div>
        </div>
      </header>

      {/* Breadcrumb trail for backtracking */}
      <BreadcrumbTrail 
        gameState={gameState.gameState}
        onBacktrack={gameState.backtrackToTurn}
        isLoading={gameState.isLoading}
      />

      {/* Main game content */}
      <main className="flex-1 flex flex-col lg:flex-row">
        {/* Story output area - always full width on top */}
        <div className="w-full p-4">
          {/* Wrapper for tooltip positioning context */}
          <div style={{ position: 'relative', zIndex: 100 }}>
            <div 
              ref={outputRef}
              className="retro-terminal retro-scrollbar max-w-none prose prose-invert bg-retro-black border-2 border-retro-green p-6 rounded min-h-96 max-h-96 lg:max-h-screen-75 overflow-y-auto"
              role="log"
              aria-live="polite"
              aria-label="Game story output"
            >
              {/* Game history */}
              {gameState.gameState.history.map((turn, index) => (
                <div key={index} className="mb-6">
                  {/* AI Response */}
                  <div className="mb-4">
                    {index === (gameState.gameState?.history.length ?? 0) - 1 ? (
                      // Current turn with typewriter effect
                      <div>
                        <div 
                          className="leading-relaxed"
                          dangerouslySetInnerHTML={{
                            __html: highlightVocabularyWords(displayedText, gameState.vocabularyManager)
                          }}
                        />
                        {isTyping && (
                          <span className="inline-block w-2 h-5 bg-retro-green ml-1 animate-blink" aria-hidden="true">
                            │
                          </span>
                        )}
                      </div>
                    ) : (
                      // Previous turns
                      <div 
                        className="leading-relaxed opacity-80"
                        dangerouslySetInnerHTML={{
                          __html: highlightVocabularyWords(turn.ai_response, gameState.vocabularyManager)
                        }}
                      />
                    )}
                  </div>

                  {/* User Input for the choice that led to the NEXT turn's response */}
                  {/* This is not shown for the very last turn as the next response is pending */}
                  {index < (gameState.gameState?.history.length ?? 0) - 1 && (
                    <div className="text-retro-amber font-mono">
                      &gt; You: {gameState.gameState.history[index + 1].user_input?.replace(/^\d+\.\s*/, '')}
                    </div>
                  )}

                  {/* Turn separator */}
                  {index < (gameState.gameState?.history.length ?? 1) - 1 && (
                    <hr className="border-retro-green opacity-30 my-4" />
                  )}
                </div>
              ))}

              {/* Scroll anchor */}
              <div ref={endOfContentRef} />
            </div>
          </div>

          {/* Skip animation button */}
          {isTyping && (
            <button
              onClick={handleSkipAnimation}
              className="mt-2 text-sm text-retro-amber hover:text-retro-green focus:outline-none focus:ring-2 focus:ring-retro-amber"
            >
              Press to skip animation ⏭️
            </button>
          )}

          {/* Choice Selection Box - Below the story */}
          {!gameState.gameState.game_over && !isTyping && (
            <div className="mt-6 p-6 border-2 border-retro-amber rounded-lg bg-retro-black max-w-4xl mx-auto">
              <h3 className="text-retro-amber text-xl font-semibold mb-6 text-center">
                🤔 What do you want to do next?
              </h3>
              
              {/* 4 Choice buttons in a 2x2 grid on larger screens */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(gameState.gameState.current_choices || [
                  "1. Continue exploring ✨",
                  "2. Look around carefully 👀", 
                  "3. Move forward slowly 👣",
                  "4. Stay where you are 🛑"
                ]).map((choice, index) => (
                  <button
                    key={index}
                    onClick={() => gameState.sendInput(choice)}
                    disabled={gameState.isLoading}
                    className={`
                      p-4 rounded border-2 border-retro-green text-left font-medium text-lg transition-all
                      bg-retro-black text-retro-green hover:bg-retro-green hover:text-retro-black
                      disabled:opacity-50 disabled:cursor-not-allowed
                      focus:outline-none focus:ring-2 focus:ring-retro-amber
                    `}
                    aria-label={`Choice ${index + 1}`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-full bg-retro-green text-retro-black flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <span className="flex-1">{choice.replace(/^\d+\.\s*/, '')}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Loading indicator */}
              {gameState.isLoading && (
                <div className="text-center mt-6">
                  <div className="inline-flex items-center space-x-2 text-retro-amber">
                    <div className="loading-spinner w-5 h-5" />
                    <span className="font-medium">Creating your next adventure...</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Game Over below story */}
          {gameState.gameState.game_over && (
            <div className="mt-6 p-6 border-2 border-retro-amber rounded-lg bg-retro-black max-w-md mx-auto">
              <div className="text-center">
                <h2 className="text-retro-amber text-2xl font-bold mb-4">
                  🎉 Adventure Complete! 🎉
                </h2>
                <p className="text-retro-green mb-6">
                  Thanks for playing! Ready for another adventure?
                </p>
                <button
                  onClick={gameState.newGame}
                  className="btn-primary"
                >
                  START NEW ADVENTURE
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Vocabulary sidebar */}
        <div className="lg:w-80 border-t lg:border-t-0 lg:border-l border-retro-green p-4">
          <VocabularyTracker vocabularyManager={gameState.vocabularyManager} />
        </div>
      </main>

      {/* Error display */}
      {gameState.error && (
        <div 
          className="fixed bottom-4 left-4 right-4 bg-red-900 border border-red-500 text-red-100 p-4 rounded z-50"
          role="alert"
          aria-live="assertive"
        >
          <div className="flex justify-between items-start">
            <span>{gameState.error}</span>
            <button
              onClick={gameState.clearError}
              className="ml-4 text-red-300 hover:text-red-100 focus:outline-none"
              aria-label="Dismiss error"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
