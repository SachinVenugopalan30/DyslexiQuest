import { useState } from 'react';
import { GameSettings } from '../App';
import { AnimatedAsciiArt } from './AnimatedAsciiArt';

interface IntroScreenProps {
  onStartGame: (genre: 'forest' | 'space' | 'dungeon' | 'mystery') => Promise<void>;
  settings: GameSettings;
}

export const IntroScreen: React.FC<IntroScreenProps> = ({ onStartGame, settings }) => {
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const genres = [
    {
      id: 'forest' as const,
      name: 'Forest Adventure',
      description: 'Explore a magical forest with friendly animals and talking trees',
      icon: '🌲',
    },
    {
      id: 'space' as const,
      name: 'Space Adventure',
      description: 'Journey through space visiting friendly planets and kind aliens',
      icon: '🚀',
    },
    {
      id: 'dungeon' as const,
      name: 'Magical Dungeon',
      description: 'Quest through friendly dungeon rooms with helpful creatures',
      icon: '✨',
    },
    {
      id: 'mystery' as const,
      name: 'Mystery Adventure',
      description: 'Help solve friendly mysteries and find missing things',
      icon: '🕵️',
    },
  ];

  const handleGenreSelect = async (genre: 'forest' | 'space' | 'dungeon' | 'mystery') => {
    setSelectedGenre(genre); // Set selected genre immediately for visual feedback
    try {
      await onStartGame(genre);
    } catch (error) {
      console.error('Failed to start game:', error);
      setSelectedGenre(null); // Reset if there's an error
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      role="main"
      aria-labelledby="intro-title"
    >
      <div className="max-w-7xl w-full">
        {/* ASCII Art Header */}
        <div className="text-center mb-8 font-mono w-full overflow-x-auto">
          <AnimatedAsciiArt skipAnimations={settings.skipAnimations} />
        </div>

        {/* Title */}
        <h1 
          id="intro-title"
          className={`text-3xl md:text-4xl font-bold text-center mb-4 text-retro-amber ${
            settings.skipAnimations ? '' : 'fade-in-up-delay-1'
          }`}
        >
          WELCOME, YOUNG ADVENTURER!
        </h1>

        {/* Subtitle */}
        <p className={`text-center text-lg mb-8 max-w-2xl mx-auto leading-relaxed ${
          settings.skipAnimations ? '' : 'fade-in-up-delay-2'
        }`}>
          Ready for an exciting text adventure? Choose your story type and begin 
          a journey full of puzzles, new words, and amazing discoveries!
        </p>

        {/* Genre Selection */}
        <div className={`space-y-4 ${settings.skipAnimations ? '' : 'fade-in-up-delay-2'}`}>
          <h2 className="text-2xl font-bold text-center mb-6 text-retro-green">
            CHOOSE YOUR ADVENTURE TYPE:
          </h2>
          
          <div className="grid md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            {genres.map((genre) => (
              <button
                key={genre.id}
                onClick={() => handleGenreSelect(genre.id)}
                disabled={selectedGenre !== null} // Disable all buttons when one is selected
                className={`p-6 border-2 focus:outline-none focus:ring-4 focus:ring-retro-green focus:ring-offset-2 focus:ring-offset-retro-black transition-all duration-300 text-left rounded group ${
                  selectedGenre === genre.id
                    ? 'bg-retro-green text-retro-black border-retro-green' // Selected state
                    : selectedGenre !== null
                    ? 'bg-retro-black border-gray-600 text-gray-600 opacity-50 cursor-not-allowed' // Disabled state
                    : 'bg-retro-black border-retro-green hover:bg-retro-green hover:text-retro-black' // Normal state
                }`}
                aria-describedby={`${genre.id}-description`}
              >
                <div className="flex items-start space-x-4">
                  <span className="text-4xl" role="img" aria-hidden="true">
                    {genre.icon}
                  </span>
                  <div className="flex-1">
                    <h3 className={`text-xl font-bold mb-2 ${
                      selectedGenre === genre.id 
                        ? 'text-retro-black' 
                        : 'text-retro-amber group-hover:text-retro-black'
                    }`}>
                      {selectedGenre === genre.id && '✓ '}{genre.name}
                    </h3>
                    <p 
                      id={`${genre.id}-description`}
                      className="text-sm leading-relaxed"
                    >
                      {genre.description}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Instructions */}
        <div className={`mt-8 p-4 bg-retro-black border border-retro-amber rounded ${
          settings.skipAnimations ? '' : 'fade-in-up-delay-3'
        }`}>
          <h3 className="text-retro-amber font-bold mb-2">📖 HOW TO PLAY:</h3>
          <ul className="text-sm space-y-1 list-none">
            <li>• Choose an adventure type to begin your story</li>
            <li>• Read each part of the story carefully</li>
            <li>• Type what you want to do next</li>
            <li>• Click on highlighted words to learn their meanings</li>
            <li>• You can go back to previous choices if needed</li>
            <li>• The game lasts up to 10 turns - make them count!</li>
          </ul>
        </div>

        {/* Accessibility Notice */}
        <div className={`mt-6 text-center text-sm text-retro-green ${
          settings.skipAnimations ? '' : 'fade-in-up-delay-3'
        }`}>
          <p>
            💡 Use the settings button (⚙️) in the top-right corner to adjust 
            text size, colors, and fonts for easier reading.
          </p>
        </div>
      </div>
    </div>
  );
};
