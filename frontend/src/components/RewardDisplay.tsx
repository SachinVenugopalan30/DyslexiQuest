import { useState, useEffect } from 'react';
import { Trophy } from 'lucide-react';

interface Reward {
  type: 'star' | 'coin' | 'badge' | 'achievement';
  name: string;
  description: string;
  icon: string;
  points: number;
}

interface PlayerProgress {
  current_segment_id: string;
  segments_completed: string[];
  correct_choices: number;
  incorrect_choices: number;
  hints_used: number;
  challenges_completed: number;
  current_difficulty: number;
  rewards_earned: Reward[];
  session_start_time: string;
  total_reading_time: number;
}

interface RewardDisplayProps {
  reward?: Reward;
  playerProgress: PlayerProgress;
  showRewardAnimation?: boolean;
  onAnimationComplete?: () => void;
}

export const RewardDisplay: React.FC<RewardDisplayProps> = ({
  reward,
  playerProgress,
  showRewardAnimation = false,
  onAnimationComplete
}) => {
  const [showAnimation, setShowAnimation] = useState(showRewardAnimation);

  useEffect(() => {
    if (showRewardAnimation) {
      setShowAnimation(true);
      const timer = setTimeout(() => {
        setShowAnimation(false);
        onAnimationComplete?.();
      }, 3000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [showRewardAnimation, onAnimationComplete]);

  const getRewardIcon = (reward: Reward) => {
    if (reward.icon) return reward.icon;
    
    switch (reward.type) {
      case 'star': return '⭐';
      case 'coin': return '🪙';
      case 'badge': return '🏆';
      case 'achievement': return '👑';
      default: return '🌟';
    }
  };

  const getTotalPoints = () => {
    return playerProgress.rewards_earned.reduce((total, r) => total + r.points, 0);
  };

  const getProgressStats = () => {
    const totalChoices = playerProgress.correct_choices + playerProgress.incorrect_choices;
    const accuracy = totalChoices > 0 ? (playerProgress.correct_choices / totalChoices) * 100 : 0;
    
    return {
      accuracy: Math.round(accuracy),
      totalStars: playerProgress.rewards_earned.filter(r => r.type === 'star').length,
      totalCoins: playerProgress.rewards_earned.filter(r => r.type === 'coin').length,
      totalBadges: playerProgress.rewards_earned.filter(r => r.type === 'badge').length,
      totalAchievements: playerProgress.rewards_earned.filter(r => r.type === 'achievement').length
    };
  };

  const stats = getProgressStats();

  return (
    <div className="reward-display">
      {/* Reward Animation */}
      {showAnimation && reward && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fade-in">
          <div className="bg-retro-black border-4 border-retro-amber rounded-lg p-8 text-center animate-bounce">
            <div className="text-6xl mb-4">{getRewardIcon(reward)}</div>
            <h2 className="text-2xl font-bold text-retro-amber mb-2">{reward.name}</h2>
            <p className="text-retro-green mb-4 dyslexia-friendly">{reward.description}</p>
            <div className="text-retro-amber font-bold">
              +{reward.points} points! 🌟
            </div>
          </div>
        </div>
      )}

      {/* Progress Display */}
      <div className="bg-retro-black border-2 border-retro-green rounded-lg p-4">
        <h3 className="text-retro-amber font-bold mb-4 flex items-center">
          <Trophy size={20} className="mr-2" />
          Your Progress
        </h3>

        {/* Points Display */}
        <div className="mb-4 text-center">
          <div className="text-3xl font-bold text-retro-amber mb-1">
            {getTotalPoints()}
          </div>
          <div className="text-sm text-retro-green">Total Points</div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <div className="text-xl text-retro-green mb-1">
              ⭐ {stats.totalStars}
            </div>
            <div className="text-xs text-retro-green opacity-80">Stars</div>
          </div>
          
          <div className="text-center">
            <div className="text-xl text-retro-green mb-1">
              🪙 {stats.totalCoins}
            </div>
            <div className="text-xs text-retro-green opacity-80">Coins</div>
          </div>
          
          <div className="text-center">
            <div className="text-xl text-retro-green mb-1">
              🏆 {stats.totalBadges}
            </div>
            <div className="text-xs text-retro-green opacity-80">Badges</div>
          </div>
          
          <div className="text-center">
            <div className="text-xl text-retro-green mb-1">
              {stats.accuracy}%
            </div>
            <div className="text-xs text-retro-green opacity-80">Accuracy</div>
          </div>
        </div>

        {/* Recent Rewards */}
        {playerProgress.rewards_earned.length > 0 && (
          <div>
            <h4 className="text-retro-amber text-sm font-bold mb-2">Recent Rewards:</h4>
            <div className="flex flex-wrap gap-2">
              {playerProgress.rewards_earned.slice(-5).map((reward, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-1 bg-retro-dark-green bg-opacity-20 rounded-full px-3 py-1 border border-retro-green"
                >
                  <span className="text-sm">{getRewardIcon(reward)}</span>
                  <span className="text-xs text-retro-green">{reward.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Encouragement Messages */}
        <div className="mt-4 text-center">
          {stats.accuracy >= 80 && (
            <div className="text-retro-amber text-sm font-medium">
              🌟 Amazing! You're doing great! 🌟
            </div>
          )}
          {stats.accuracy >= 60 && stats.accuracy < 80 && (
            <div className="text-retro-green text-sm">
              👏 Good job! Keep it up! 👏
            </div>
          )}
          {stats.accuracy < 60 && stats.accuracy > 0 && (
            <div className="text-retro-green text-sm">
              💪 You're learning! Every try makes you better! 💪
            </div>
          )}
          {playerProgress.correct_choices === 0 && playerProgress.incorrect_choices === 0 && (
            <div className="text-retro-green text-sm">
              🚀 Ready for an adventure? Let's go! 🚀
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface FeedbackDisplayProps {
  feedback: string;
  isCorrect: boolean;
  hint?: string;
  onContinue?: () => void;
  showContinueButton?: boolean;
}

export const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({
  feedback,
  isCorrect,
  hint,
  onContinue,
  showContinueButton = true
}) => {
  return (
    <div className={`feedback-display border-2 rounded-lg p-4 mb-4 ${
      isCorrect ? 'border-green-500 bg-green-500 bg-opacity-10' : 'border-yellow-500 bg-yellow-500 bg-opacity-10'
    }`}>
      <div className="flex items-start space-x-3">
        <div className="text-2xl">
          {isCorrect ? '🎉' : '💭'}
        </div>
        <div className="flex-1">
          <p className={`font-medium mb-2 dyslexia-friendly ${
            isCorrect ? 'text-green-400' : 'text-yellow-400'
          }`} style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>
            {feedback}
          </p>
          
          {hint && !isCorrect && (
            <p className="text-retro-green text-sm dyslexia-friendly opacity-90">
              💡 {hint}
            </p>
          )}
          
          {showContinueButton && onContinue && (
            <button
              onClick={onContinue}
              className="btn-primary mt-3 px-4 py-2"
            >
              {isCorrect ? 'Continue! 🚀' : 'Try Again! 💪'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
