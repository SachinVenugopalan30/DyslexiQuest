import { useState } from 'react';
import { RotateCcw } from 'lucide-react';

interface ChildFriendlyInputProps {
  onSubmit: (input: string) => Promise<void>;
  isDisabled: boolean;
  isLoading: boolean;
  error: string | null;
  onClearError: () => void;
  gameOver: boolean;
  onNewGame: () => void;
  onEndGame: () => Promise<void>;
  currentChoices?: string[];
}

export const ChildFriendlyInput: React.FC<ChildFriendlyInputProps> = ({
  onSubmit,
  isDisabled,
  isLoading,
  error,
  onClearError,
  gameOver,
  onNewGame,
  onEndGame,
  currentChoices = [
    "1. Continue exploring ✨",
    "2. Look around carefully 👀", 
    "3. Move forward slowly 👣",
    "4. Stay where you are 🛑"
  ]
}) => {
  const [selectedChoice, setSelectedChoice] = useState<string>('');

  const handleChoiceSelect = async (_choiceNumber: number, choiceText: string) => {
    if (!isDisabled) {
      setSelectedChoice(choiceText);
      if (error) {
        onClearError();
      }
      // Submit the choice immediately when clicked
      await onSubmit(choiceText);
      setSelectedChoice('');
    }
  };

  if (gameOver) {
    return (
      <div className="p-6 bg-gradient-to-r from-purple-100 to-blue-100 border-t-4 border-purple-400">
        <div className="text-center max-w-md mx-auto">
          <h2 className="text-purple-700 text-2xl font-bold mb-4">
            🎉 Amazing Job! You completed your reading adventure! 🎉
          </h2>
          <p className="text-purple-600 mb-6">
            You're becoming a super strong reader! Ready for another adventure?
          </p>
          <button
            onClick={onNewGame}
            className="bg-purple-500 hover:bg-purple-600 text-white px-8 py-3 rounded-xl font-bold text-lg shadow-lg transition-colors flex items-center mx-auto space-x-2"
          >
            <RotateCcw className="w-5 h-5" />
            <span>START NEW ADVENTURE</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white border-t-4 border-blue-400">
      <div className="max-w-4xl mx-auto">
        <div className="mb-4">
          <h3 className="text-xl font-semibold text-purple-700 mb-2 text-center">
            🤔 What do you want to do next?
          </h3>
          <p className="text-purple-600 text-center text-sm">
            Click on the choice you like best! 
          </p>
        </div>

        {/* Choice buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {currentChoices.map((choice, index) => {
            const choiceNumber = index + 1;
            const isSelected = selectedChoice === choice;
            
            return (
              <button
                key={index}
                onClick={() => handleChoiceSelect(choiceNumber, choice)}
                disabled={isDisabled || isLoading}
                className={`
                  p-4 rounded-xl border-2 text-left font-medium text-lg transition-all
                  ${isSelected 
                    ? 'bg-green-100 border-green-400 text-green-800' 
                    : 'bg-gray-50 border-gray-300 text-gray-800 hover:bg-blue-50 hover:border-blue-400'
                  }
                  ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:shadow-md'}
                  focus:outline-none focus:ring-4 focus:ring-blue-200
                `}
                aria-label={`Choice ${choiceNumber}: ${choice}`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center font-bold text-white
                    ${isSelected ? 'bg-green-500' : 'bg-blue-500'}
                  `}>
                    {choiceNumber}
                  </div>
                  <span className="flex-1">{choice.replace(/^\d+\.\s*/, '')}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Loading indicator */}
        {isLoading && (
          <div className="text-center">
            <div className="inline-flex items-center space-x-2 text-purple-600">
              <div className="loading-spinner w-5 h-5" />
              <span className="font-medium">Creating your next adventure...</span>
            </div>
          </div>
        )}

        {/* Encouragement message */}
        <div className="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-xl p-4 text-center">
          <p className="text-orange-700 font-medium">
            🌟 You're doing great! Take your time and choose what feels right to you! 🌟
          </p>
        </div>

        {/* End game option (small and unobtrusive) */}
        <div className="text-center mt-4">
          <button
            onClick={onEndGame}
            disabled={isLoading}
            className="text-sm text-gray-500 hover:text-gray-700 underline focus:outline-none"
          >
            Stop playing for now
          </button>
        </div>
      </div>
    </div>
  );
};
