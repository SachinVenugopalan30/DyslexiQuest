// Vocabulary tracking and educational features

export interface VocabularyWord {
  word: string;
  definition: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  example?: string;
  synonyms?: string[];
  phonetic?: string;
}

export interface VocabularyProgress {
  words_learned: string[];
  definitions_viewed: string[];
  words_mastered: string[];
  total_games_played: number;
  last_played: number;
  current_streak: number;
  best_streak: number;
}

// Sample vocabulary database for the game
export const vocabularyDatabase: Record<string, VocabularyWord> = {
  'adventure': {
    word: 'adventure',
    definition: 'An exciting or dangerous experience or journey',
    difficulty: 'easy',
    category: 'general',
    example: 'Going on an adventure through the forest was thrilling!',
    synonyms: ['journey', 'expedition', 'quest'],
    phonetic: '/ədˈven(t)SHər/'
  },
  'mysterious': {
    word: 'mysterious',
    definition: 'Strange, unknown, or difficult to understand',
    difficulty: 'medium',
    category: 'descriptive',
    example: 'The mysterious door had no handle or keyhole.',
    synonyms: ['puzzling', 'unknown', 'secretive'],
    phonetic: '/məˈstirēəs/'
  },
  'courage': {
    word: 'courage',
    definition: 'The ability to do something brave or difficult',
    difficulty: 'medium',
    category: 'emotion',
    example: 'It took courage to enter the dark cave.',
    synonyms: ['bravery', 'boldness', 'valor'],
    phonetic: '/ˈkərij/'
  },
  'ancient': {
    word: 'ancient',
    definition: 'Very old, from long ago in history',
    difficulty: 'easy',
    category: 'time',
    example: 'The ancient castle was built hundreds of years ago.',
    synonyms: ['old', 'historic', 'aged'],
    phonetic: '/ˈān(t)SHənt/'
  },
  'discover': {
    word: 'discover',
    definition: 'To find something for the first time',
    difficulty: 'easy',
    category: 'action',
    example: 'We might discover treasure in the hidden room.',
    synonyms: ['find', 'uncover', 'reveal'],
    phonetic: '/dəˈskəvər/'
  },
  'enchanted': {
    word: 'enchanted',
    definition: 'Having magical powers or under a magic spell',
    difficulty: 'medium',
    category: 'magic',
    example: 'The enchanted sword glowed with blue light.',
    synonyms: ['magical', 'bewitched', 'spellbound'],
    phonetic: '/ənˈCHan(t)əd/'
  },
  'riddle': {
    word: 'riddle',
    definition: 'A puzzle or question that needs clever thinking to solve',
    difficulty: 'medium',
    category: 'puzzle',
    example: 'The sphinx asked a difficult riddle.',
    synonyms: ['puzzle', 'mystery', 'brain teaser'],
    phonetic: '/ˈridl/'
  },
  'treasure': {
    word: 'treasure',
    definition: 'Valuable things like gold, jewels, or precious objects',
    difficulty: 'easy',
    category: 'objects',
    example: 'The pirates buried their treasure on the island.',
    synonyms: ['riches', 'valuables', 'wealth'],
    phonetic: '/ˈtreSHər/'
  },
  'wisdom': {
    word: 'wisdom',
    definition: 'Knowledge and good judgment gained from experience',
    difficulty: 'hard',
    category: 'abstract',
    example: 'The old wizard shared his wisdom with young adventurers.',
    synonyms: ['knowledge', 'insight', 'understanding'],
    phonetic: '/ˈwizdəm/'
  },
  'labyrinth': {
    word: 'labyrinth',
    definition: 'A complicated network of paths; a maze',
    difficulty: 'hard',
    category: 'places',
    example: 'Getting lost in the labyrinth was scary but exciting.',
    synonyms: ['maze', 'network', 'puzzle'],
    phonetic: '/ˈlabəˌrinTH/'
  }
};

// Vocabulary management class
export class VocabularyManager {
  private progress: VocabularyProgress;

  constructor(initialProgress?: VocabularyProgress) {
    this.progress = initialProgress || {
      words_learned: [],
      definitions_viewed: [],
      words_mastered: [],
      total_games_played: 0,
      last_played: Date.now(),
      current_streak: 0,
      best_streak: 0,
    };
  }

  // Add a new word to the learning list
  addLearnedWord(word: string): void {
    if (!this.progress.words_learned.includes(word.toLowerCase())) {
      this.progress.words_learned.push(word.toLowerCase());
      this.updateStreak();
    }
  }

  // Mark that a definition was viewed
  markDefinitionViewed(word: string): void {
    if (!this.progress.definitions_viewed.includes(word.toLowerCase())) {
      this.progress.definitions_viewed.push(word.toLowerCase());
    }
  }

  // Mark a word as mastered (viewed multiple times, used correctly)
  markWordMastered(word: string): void {
    const normalizedWord = word.toLowerCase();
    if (!this.progress.words_mastered.includes(normalizedWord)) {
      this.progress.words_mastered.push(normalizedWord);
    }
  }

  // Get vocabulary word information
  getWordInfo(word: string): VocabularyWord | null {
    return vocabularyDatabase[word.toLowerCase()] || null;
  }

  // Get words by difficulty level
  getWordsByDifficulty(difficulty: 'easy' | 'medium' | 'hard'): VocabularyWord[] {
    return Object.values(vocabularyDatabase).filter(
      (word) => word.difficulty === difficulty
    );
  }

  // Get learning progress statistics
  getProgressStats(): {
    totalWordsLearned: number;
    totalDefinitionsViewed: number;
    wordsMastered: number;
    currentStreak: number;
    bestStreak: number;
    completionPercentage: number;
  } {
    const totalWords = Object.keys(vocabularyDatabase).length;
    
    return {
      totalWordsLearned: this.progress.words_learned.length,
      totalDefinitionsViewed: this.progress.definitions_viewed.length,
      wordsMastered: this.progress.words_mastered.length,
      currentStreak: this.progress.current_streak,
      bestStreak: this.progress.best_streak,
      completionPercentage: Math.round(
        (this.progress.words_learned.length / totalWords) * 100
      ),
    };
  }

  // Update learning streak
  private updateStreak(): void {
    this.progress.current_streak += 1;
    if (this.progress.current_streak > this.progress.best_streak) {
      this.progress.best_streak = this.progress.current_streak;
    }
  }

  // Reset current streak (when game ends or user takes break)
  resetCurrentStreak(): void {
    this.progress.current_streak = 0;
  }

  // Get current progress object
  getProgress(): VocabularyProgress {
    return { ...this.progress };
  }

  // Update progress
  updateProgress(newProgress: Partial<VocabularyProgress>): void {
    this.progress = { ...this.progress, ...newProgress };
  }
}

// Utility function to extract vocabulary words from text
export const extractVocabularyWords = (text: string): string[] => {
  const words = text
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 3);

  return words.filter(word => vocabularyDatabase[word]);
};

// Create a simple definition tooltip
export const createDefinitionTooltip = (
  word: string,
  onView?: (word: string) => void
): string => {
  const wordInfo = vocabularyDatabase[word.toLowerCase()];
  if (!wordInfo) return word;

  if (onView) {
    onView(word);
  }

  return `<span class="vocabulary-word" data-word="${word}">
    ${word}
    <span class="vocabulary-tooltip">
      <strong>${wordInfo.word}</strong><br>
      ${wordInfo.definition}
      ${wordInfo.example ? `<br><em>Example: ${wordInfo.example}</em>` : ''}
    </span>
  </span>`;
};

// Highlight vocabulary words in text (avoiding nested highlighting)
export const highlightVocabularyWords = (
  text: string,
  vocabularyManager?: VocabularyManager
): string => {
  // First, create a safe version of tooltip content that won't be re-processed
  const createSafeTooltip = (word: string): string => {
    const wordInfo = vocabularyDatabase[word.toLowerCase()];
    if (!wordInfo) return word;

    if (vocabularyManager) {
      vocabularyManager.addLearnedWord(word);
    }

    // Replace vocabulary words in tooltip content with placeholder to prevent nested highlighting
    let safeDefinition = wordInfo.definition;
    let safeExample = wordInfo.example || '';
    
    Object.keys(vocabularyDatabase).forEach(vocabWord => {
      const safeRegex = new RegExp(`\\b${vocabWord}\\b`, 'gi');
      safeDefinition = safeDefinition.replace(safeRegex, `__VOCAB_${vocabWord.toUpperCase()}__`);
      safeExample = safeExample.replace(safeRegex, `__VOCAB_${vocabWord.toUpperCase()}__`);
    });

    return `<span class="vocabulary-word" data-word="${word}">
      ${word}
      <span class="vocabulary-tooltip">
        <strong>${wordInfo.word}</strong><br>
        ${safeDefinition}
        ${safeExample ? `<br><em>Example: ${safeExample}</em>` : ''}
      </span>
    </span>`;
  };

  let highlightedText = text;

  // Sort vocabulary words by length (longest first) to avoid partial matches
  const sortedWords = Object.keys(vocabularyDatabase).sort((a, b) => b.length - a.length);

  sortedWords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    highlightedText = highlightedText.replace(regex, (match) => {
      return createSafeTooltip(match);
    });
  });

  // Restore the vocabulary words in tooltip content
  Object.keys(vocabularyDatabase).forEach(word => {
    const placeholderRegex = new RegExp(`__VOCAB_${word.toUpperCase()}__`, 'g');
    highlightedText = highlightedText.replace(placeholderRegex, word);
  });

  return highlightedText;
};

// Generate age-appropriate vocabulary suggestions
export const generateVocabularySuggestions = (
  currentWords: string[],
  targetDifficulty: 'easy' | 'medium' | 'hard' = 'medium',
  count: number = 3
): VocabularyWord[] => {
  const availableWords = Object.values(vocabularyDatabase)
    .filter(word => 
      word.difficulty === targetDifficulty && 
      !currentWords.includes(word.word.toLowerCase())
    );

  // Shuffle and return requested count
  const shuffled = availableWords.sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
};
