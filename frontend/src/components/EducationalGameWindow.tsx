import { useState } from 'react';
import { GameSettings } from '../App';
import { UseGameStateReturn } from '../hooks/useGameState';
import { StorySegmentDisplay } from './StorySegmentDisplay';
import { RewardDisplay } from './RewardDisplay';
import { VocabularyTracker } from './VocabularyTracker';
import { AccessibilityControls } from './AccessibilityControls';
import { ChildFriendlyInput } from './ChildFriendlyInput';

interface EducationalGameWindowProps {
  gameState: UseGameStateReturn;
  settings: GameSettings;
  onSettingChange: <K extends keyof GameSettings>(key: K, value: GameSettings[K]) => void;
}

export const EducationalGameWindow: React.FC<EducationalGameWindowProps> = ({ 
  gameState, 
  settings, 
  onSettingChange 
}) => {
  const [showReward, setShowReward] = useState(false);
  const [currentReward, setCurrentReward] = useState<any>(null);

  // Mock educational game state - in real implementation this would come from backend
  const mockGameSession = {
    currentSegment: {
      id: "segment_1",
      story: "You discover a ✨magical garden✨ where flowers sing beautiful songs! A friendly butterfly 🦋 shows you sparkling treasures hidden among the colorful petals.",
      multipleChoices: [
        {
          id: "A",
          text: "Follow the butterfly 🦋",
          isCorrect: true,
          feedback: "Excellent choice! The butterfly leads you to wonderful discoveries! 🌟"
        },
        {
          id: "B", 
          text: "Listen to singing flowers 🌺",
          isCorrect: false,
          feedback: "The flowers have lovely songs! But maybe the butterfly has something special to show you. Try again! 🎵"
        },
        {
          id: "C",
          text: "Explore the sparkling pond ✨", 
          isCorrect: false,
          feedback: "The pond is beautiful! But the butterfly seems excited about something. What could it be? ✨"
        },
        {
          id: "D",
          text: "Look for hidden treasure 💰",
          isCorrect: false,
          feedback: "Good thinking! There might be treasure nearby. The butterfly knows where to find it! 💰"
        }
      ],
      wordChallenge: {
        type: "word_completion",
        targetWord: "garden",
        prompt: "Complete this word: g_rd_n (a place where flowers grow)",
        hint: "Think about where you plant flowers and vegetables! 🌺"
      }
    },
    playerProgress: {
      segmentsCompleted: 2,
      totalSegments: 7,
      correctChoices: 5,
      challengesCompleted: 3,
      rewardsEarned: [
        { type: "star" as const, name: "Bright Star", description: "Great choice!", icon: "⭐", points: 10 },
        { type: "coin" as const, name: "Golden Coin", description: "Word master!", icon: "🪙", points: 25 }
      ]
    },
    gameComplete: false
  };

  const handleChoiceSelect = (choiceId: string) => {
    const choice = mockGameSession.currentSegment.multipleChoices.find(c => c.id === choiceId);
    if (!choice) return;

    // Show feedback and potentially reward
    if (choice.isCorrect) {
      const reward = { type: "star", name: "Bright Star", icon: "⭐", points: 10 };
      setCurrentReward(reward);
      setShowReward(true);
      
      // Hide reward after 3 seconds
      setTimeout(() => {
        setShowReward(false);
        setCurrentReward(null);
      }, 3000);
    }
  };

  const handleChallengeSubmit = (answer: string) => {
    const isCorrect = answer.toLowerCase() === mockGameSession.currentSegment.wordChallenge.targetWord.toLowerCase();
    
    if (isCorrect) {
      const reward = { type: "coin", name: "Word Master", icon: "🪙", points: 25 };
      setCurrentReward(reward);
      setShowReward(true);
      
      setTimeout(() => {
        setShowReward(false);
        setCurrentReward(null);
      }, 3000);
    }
    
    return isCorrect;
  };

  if (!gameState.gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-100 to-purple-100">
        <div className="text-center">
          <div className="loading-spinner w-12 h-12 mx-auto mb-4"></div>
          <p className="text-lg text-purple-700 font-semibold">Starting your reading adventure...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md p-4">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-2 sm:space-y-0">
          <div>
            <h1 className="text-2xl font-bold text-purple-700 flex items-center">
              📚 Reading Adventure 
              <span className="ml-2 text-lg text-purple-500">
                - {gameState.gameState.genre.charAt(0).toUpperCase() + gameState.gameState.genre.slice(1)}
              </span>
            </h1>
            <div className="flex items-center mt-1 space-x-4">
              <p className="text-sm text-gray-600">
                Story {mockGameSession.playerProgress.segmentsCompleted + 1} of {mockGameSession.playerProgress.totalSegments}
              </p>
              
              {/* Progress bar */}
              <div className="flex-1 max-w-48">
                <div className="bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${(mockGameSession.playerProgress.segmentsCompleted / mockGameSession.playerProgress.totalSegments) * 100}%` 
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Score display */}
            <div className="bg-yellow-100 px-3 py-1 rounded-full flex items-center space-x-2">
              <span className="text-lg">⭐</span>
              <span className="font-semibold text-yellow-700">
                {mockGameSession.playerProgress.rewardsEarned.reduce((sum, reward) => sum + reward.points, 0)} points
              </span>
            </div>

            {/* New Game button */}
            <button
              onClick={gameState.newGame}
              className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              New Adventure
            </button>

            {/* Accessibility Controls */}
            <AccessibilityControls 
              settings={settings}
              onSettingChange={onSettingChange}
              inline={true}
            />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto p-4 grid lg:grid-cols-3 gap-6">
        {/* Story and interaction area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Current story segment */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <StorySegmentDisplay
              segment={{
                id: mockGameSession.currentSegment.id,
                text: mockGameSession.currentSegment.story,
                multiple_choices: mockGameSession.currentSegment.multipleChoices.map(choice => ({
                  id: choice.id,
                  text: choice.text,
                  is_correct: choice.isCorrect,
                  feedback: choice.feedback,
                  visual_cue: { icon: '✨', description: '', position: 'before' },
                  difficulty_adjustment: 0
                })),
                word_challenge: {
                  type: 'completion' as const,
                  instruction: mockGameSession.currentSegment.wordChallenge.prompt,
                  word: mockGameSession.currentSegment.wordChallenge.targetWord,
                  correct_answer: mockGameSession.currentSegment.wordChallenge.targetWord,
                  hint: mockGameSession.currentSegment.wordChallenge.hint,
                  visual_cue: { icon: '🌸', description: 'garden', position: 'before' },
                  difficulty_level: 1

                },
                visual_cues: [{ icon: '✨', description: 'magic', position: 'inline' }],
                vocabulary_words: ['garden', 'magical', 'butterfly'],
                difficulty_level: 1,
                estimated_reading_time: 45,

              }}
              onChoice={handleChoiceSelect}
              onChallenge={handleChallengeSubmit}
              textToSpeechEnabled={settings.fontFamily === 'accessible'}
            />
          </div>

          {/* Session progress */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-purple-700 mb-4 flex items-center">
              📊 Your Progress Today
            </h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {mockGameSession.playerProgress.segmentsCompleted}
                </div>
                <div className="text-sm text-gray-600">Stories Read</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {mockGameSession.playerProgress.correctChoices}
                </div>
                <div className="text-sm text-gray-600">Great Choices</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {mockGameSession.playerProgress.challengesCompleted}
                </div>
                <div className="text-sm text-gray-600">Word Challenges</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {mockGameSession.playerProgress.rewardsEarned.length}
                </div>
                <div className="text-sm text-gray-600">Rewards Earned</div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Vocabulary Tracker */}
          <div className="bg-white rounded-xl shadow-lg">
            <VocabularyTracker vocabularyManager={gameState.vocabularyManager} />
          </div>

          {/* Recent Rewards */}
          <div className="bg-white rounded-xl shadow-lg p-4">
            <h3 className="text-lg font-semibold text-purple-700 mb-3 flex items-center">
              🏆 Recent Rewards
            </h3>
            
            <div className="space-y-2">
              {mockGameSession.playerProgress.rewardsEarned.slice(-3).map((reward, index) => (
                <div key={index} className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg">
                  <span className="text-2xl">{reward.icon}</span>
                  <div>
                    <div className="font-medium text-gray-800">{reward.name}</div>
                    <div className="text-sm text-gray-600">+{reward.points} points</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Encouragement */}
          <div className="bg-gradient-to-br from-pink-100 to-purple-100 rounded-xl shadow-lg p-4">
            <h3 className="text-lg font-semibold text-purple-700 mb-2 flex items-center">
              💪 You're Doing Great!
            </h3>
            <p className="text-purple-600 text-sm">
              Keep reading and exploring! Every story makes you a stronger reader. 
              You're building amazing skills! 🌟
            </p>
          </div>
        </div>
      </main>

      {/* Child-friendly input section */}
      <ChildFriendlyInput
        onSubmit={gameState.sendInput}
        isDisabled={gameState.isLoading || gameState.gameState.game_over}
        isLoading={gameState.isLoading}
        error={gameState.error}
        onClearError={gameState.clearError}
        gameOver={gameState.gameState.game_over}
        onNewGame={gameState.newGame}
        onEndGame={gameState.endGame}
        currentChoices={mockGameSession.currentSegment.multipleChoices.map((choice, index) => 
          `${index + 1}. ${choice.text}`
        )}
      />

      {/* Reward popup */}
      {showReward && currentReward && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <RewardDisplay
            reward={currentReward}
            playerProgress={{
              current_segment_id: mockGameSession.currentSegment.id,
              segments_completed: [],
              correct_choices: mockGameSession.playerProgress.correctChoices,
              incorrect_choices: 0,
              hints_used: 0,
              challenges_completed: mockGameSession.playerProgress.challengesCompleted,
              current_difficulty: 2,
              rewards_earned: mockGameSession.playerProgress.rewardsEarned,
              session_start_time: new Date().toISOString(),
              total_reading_time: 300
            }}
            showRewardAnimation={true}
            onAnimationComplete={() => {
              setShowReward(false);
              setCurrentReward(null);
            }}
          />
        </div>
      )}

      {/* Error display */}
      {gameState.error && (
        <div className="fixed bottom-4 left-4 right-4 bg-red-100 border border-red-300 text-red-800 p-4 rounded-xl shadow-lg z-50">
          <div className="flex justify-between items-start">
            <span className="font-medium">{gameState.error}</span>
            <button
              onClick={gameState.clearError}
              className="ml-4 text-red-600 hover:text-red-800 focus:outline-none text-xl"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
