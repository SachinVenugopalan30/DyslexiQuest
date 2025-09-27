import { VocabularyManager } from '../utils/vocabulary';
import { BookOpen, Trophy, TrendingUp, Star } from 'lucide-react';

interface VocabularyTrackerProps {
  vocabularyManager: VocabularyManager;
}

export const VocabularyTracker: React.FC<VocabularyTrackerProps> = ({ vocabularyManager }) => {
  const stats = vocabularyManager.getProgressStats();

  return (
    <div className="space-y-4">
      <h2 className="text-retro-amber text-lg font-bold flex items-center space-x-2">
        <BookOpen className="w-5 h-5" />
        <span>VOCABULARY PROGRESS</span>
      </h2>

      {/* Progress Overview */}
      <div className="bg-retro-black border-2 border-retro-green p-4 rounded">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-retro-green mb-1">
              {stats.totalWordsLearned}
            </div>
            <div className="text-xs text-retro-amber">Words Learned</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-retro-green mb-1">
              {stats.wordsMastered}
            </div>
            <div className="text-xs text-retro-amber">Words Mastered</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-retro-green mb-1">
              {stats.currentStreak}
            </div>
            <div className="text-xs text-retro-amber flex items-center justify-center space-x-1">
              <TrendingUp className="w-3 h-3" />
              <span>Current Streak</span>
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-retro-green mb-1">
              {stats.bestStreak}
            </div>
            <div className="text-xs text-retro-amber flex items-center justify-center space-x-1">
              <Trophy className="w-3 h-3" />
              <span>Best Streak</span>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-retro-amber mb-1">
            <span>Learning Progress</span>
            <span>{stats.completionPercentage}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-bar-fill"
              style={{ width: `${stats.completionPercentage}%` }}
              role="progressbar"
              aria-valuenow={stats.completionPercentage}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`Vocabulary learning progress: ${stats.completionPercentage}% complete`}
            />
          </div>
        </div>
      </div>

      {/* Achievement Badges */}
      <div className="bg-retro-black border border-retro-green p-3 rounded">
        <h3 className="text-retro-amber text-sm font-bold mb-2 flex items-center space-x-1">
          <Star className="w-4 h-4" />
          <span>ACHIEVEMENTS</span>
        </h3>
        
        <div className="grid grid-cols-2 gap-2 text-xs">
          {/* First Word */}
          <div className={`p-2 border rounded text-center ${
            stats.totalWordsLearned >= 1 
              ? 'border-retro-green text-retro-green' 
              : 'border-gray-600 text-gray-500'
          }`}>
            <div className="text-lg mb-1">📚</div>
            <div>First Word!</div>
          </div>

          {/* Word Explorer */}
          <div className={`p-2 border rounded text-center ${
            stats.totalWordsLearned >= 10 
              ? 'border-retro-green text-retro-green' 
              : 'border-gray-600 text-gray-500'
          }`}>
            <div className="text-lg mb-1">🗺️</div>
            <div>Word Explorer</div>
            <div className="text-xs opacity-75">(10 words)</div>
          </div>

          {/* Vocabulary Master */}
          <div className={`p-2 border rounded text-center ${
            stats.wordsMastered >= 5 
              ? 'border-retro-green text-retro-green' 
              : 'border-gray-600 text-gray-500'
          }`}>
            <div className="text-lg mb-1">👑</div>
            <div>Word Master</div>
            <div className="text-xs opacity-75">(5 mastered)</div>
          </div>

          {/* Streak Champion */}
          <div className={`p-2 border rounded text-center ${
            stats.bestStreak >= 5 
              ? 'border-retro-green text-retro-green' 
              : 'border-gray-600 text-gray-500'
          }`}>
            <div className="text-lg mb-1">🔥</div>
            <div>Streak Champion</div>
            <div className="text-xs opacity-75">(5 streak)</div>
          </div>
        </div>
      </div>

      {/* Recent Words */}
      <div className="bg-retro-black border border-retro-green p-3 rounded">
        <h3 className="text-retro-amber text-sm font-bold mb-2">RECENT WORDS</h3>
        
        {stats.totalWordsLearned > 0 ? (
          <div className="space-y-1 text-xs">
            {vocabularyManager.getProgress().words_learned.slice(-5).map((word, index) => {
              const wordInfo = vocabularyManager.getWordInfo(word);
              return (
                <div key={index} className="p-2 border border-retro-green border-opacity-30 rounded">
                  <div className="font-medium text-retro-green">{word}</div>
                  {wordInfo && (
                    <div className="text-retro-amber opacity-75 mt-1">
                      {wordInfo.definition}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-xs text-retro-green opacity-75 text-center py-4">
            Start your adventure to learn new words!
          </p>
        )}
      </div>

      {/* Tips */}
      <div className="bg-retro-black border border-retro-amber p-3 rounded">
        <h3 className="text-retro-amber text-sm font-bold mb-2">💡 LEARNING TIPS</h3>
        <ul className="text-xs text-retro-green space-y-1">
          <li>• Hover over highlighted words for definitions</li>
          <li>• Try using new words in your responses</li>
          <li>• Build streaks by learning consistently</li>
          <li>• Master words by seeing them multiple times</li>
        </ul>
      </div>
    </div>
  );
};
