import { GameState } from '../utils/api';
import { ChevronRight, RotateCcw } from 'lucide-react';

interface BreadcrumbTrailProps {
  gameState: GameState;
  onBacktrack: (turn: number) => Promise<void>;
  isLoading: boolean;
}

export const BreadcrumbTrail: React.FC<BreadcrumbTrailProps> = ({
  gameState,
  onBacktrack,
  isLoading,
}) => {
  const MAX_BACKTRACK_COUNT = 2;
  const canBacktrack = gameState.backtrack_count < MAX_BACKTRACK_COUNT && gameState.history.length > 1;
  const remainingBacktracks = MAX_BACKTRACK_COUNT - gameState.backtrack_count;

  if (gameState.history.length <= 1) {
    return null;
  }

  return (
    <div className="border-b border-retro-green p-2 bg-retro-black">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
        {/* Breadcrumb trail */}
        <div className="flex items-center space-x-1 overflow-x-auto">
          <span className="text-xs text-retro-amber font-medium whitespace-nowrap">STORY PATH:</span>
          <div className="flex items-center space-x-1 min-w-0">
            {gameState.history.slice(-5).map((turn, index, array) => {
              const actualTurn = gameState.history.length - array.length + index + 1;
              const isLast = index === array.length - 1;
              const isCurrent = actualTurn === gameState.turn;
              
              return (
                <div key={turn.turn} className="flex items-center space-x-1">
                  <button
                    onClick={() => canBacktrack && !isLast ? onBacktrack(actualTurn) : undefined}
                    disabled={isLoading || !canBacktrack || isLast}
                    className={`breadcrumb-item text-xs px-2 py-1 rounded ${
                      isCurrent
                        ? 'bg-retro-green text-retro-black font-bold'
                        : canBacktrack && !isLast
                        ? 'text-retro-green hover:bg-retro-green hover:text-retro-black cursor-pointer'
                        : 'text-retro-green opacity-50 cursor-not-allowed'
                    }`}
                    aria-label={
                      isLast 
                        ? `Current turn ${actualTurn}`
                        : canBacktrack 
                        ? `Go back to turn ${actualTurn}`
                        : `Turn ${actualTurn} (cannot go back)`
                    }
                  >
                    {actualTurn}
                  </button>
                  {!isLast && (
                    <ChevronRight className="w-3 h-3 text-retro-amber" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Backtrack info */}
        <div className="flex items-center space-x-2 text-xs">
          <RotateCcw className="w-3 h-3 text-retro-amber" />
          <span className="text-retro-amber whitespace-nowrap">
            {canBacktrack 
              ? `${remainingBacktracks} rewind${remainingBacktracks !== 1 ? 's' : ''} left`
              : 'No rewinds left'
            }
          </span>
        </div>
      </div>

      {/* Instructions */}
      {canBacktrack && (
        <div className="mt-2 text-xs text-retro-green opacity-75">
          💡 Click on previous turn numbers to go back and try different choices
        </div>
      )}
    </div>
  );
};
