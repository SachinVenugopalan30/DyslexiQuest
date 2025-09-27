import { useState } from 'react';
import { Send, RotateCcw, Square } from 'lucide-react';

interface InputBoxProps {
  onSubmit: (input: string) => Promise<void>;
  isDisabled: boolean;
  isLoading: boolean;
  error: string | null;
  onClearError: () => void;
  gameOver: boolean;
  onNewGame: () => void;
  onEndGame: () => Promise<void>;
}

export const InputBox: React.FC<InputBoxProps> = ({
  onSubmit,
  isDisabled,
  isLoading,
  error,
  onClearError,
  gameOver,
  onNewGame,
  onEndGame,
}) => {
  const [input, setInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isDisabled) {
      await onSubmit(input.trim());
      setInput('');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (error) {
      onClearError();
    }
  };

  if (gameOver) {
    return (
      <div className="p-4 bg-retro-black border-t-2 border-retro-green">
        <div className="text-center">
          <h2 className="text-retro-amber text-xl font-bold mb-4">
            🎮 GAME OVER - Thanks for playing! 🎮
          </h2>
          <div className="space-x-4">
            <button
              onClick={onNewGame}
              className="btn-primary"
            >
              <RotateCcw className="w-4 h-4 mr-2 inline" />
              START NEW ADVENTURE
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 bg-retro-black">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col space-y-2">
          <label htmlFor="user-input" className="text-sm font-medium">
            What do you want to do next?
          </label>
          <div className="relative">
            <textarea
              id="user-input"
              value={input}
              onChange={handleInputChange}
              disabled={isDisabled}
              placeholder={isLoading ? "Processing..." : "Type your action here..."}
              className="w-full p-3 bg-retro-black border-2 border-retro-green text-retro-green placeholder-retro-green placeholder-opacity-50 focus:outline-none focus:ring-2 focus:ring-retro-green focus:border-transparent resize-none font-mono"
              rows={3}
              maxLength={200}
              aria-describedby="input-help"
            />
            <div className="absolute bottom-2 right-2 text-xs text-retro-green opacity-50">
              {input.length}/200
            </div>
          </div>
          <p id="input-help" className="text-xs text-retro-green opacity-75">
            Describe what you want to do. Be creative! You can explore, talk to characters, use items, or solve puzzles.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            type="submit"
            disabled={isDisabled || !input.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="loading-spinner w-4 h-4" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>SUBMIT ACTION</span>
              </>
            )}
          </button>

          <div className="flex space-x-2">
            <button
              type="button"
              onClick={onEndGame}
              disabled={isLoading}
              className="btn-secondary text-sm flex items-center space-x-1"
            >
              <Square className="w-3 h-3" />
              <span>END GAME</span>
            </button>
          </div>
        </div>
      </form>

      {/* Quick action suggestions */}
      <div className="mt-4 p-3 bg-retro-black border border-retro-green rounded">
        <h3 className="text-retro-amber text-sm font-medium mb-2">💡 Quick Ideas:</h3>
        <div className="flex flex-wrap gap-2">
          {[
            "Look around",
            "Go north",
            "Examine item",
            "Talk to character",
            "Use magic",
            "Open door"
          ].map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => setInput(suggestion)}
              disabled={isDisabled}
              className="px-2 py-1 text-xs border border-retro-green text-retro-green hover:bg-retro-green hover:text-retro-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
