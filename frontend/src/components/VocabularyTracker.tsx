import { VocabularyManager } from '../utils/vocabulary';
import { BookOpen, Trophy, TrendingUp } from 'lucide-react';

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
    </div>
  );
};
