import { GameState, GameTurn } from './api';

const STORAGE_KEYS = {
  GAME_STATE: 'retro-adventure-game-state',
  GAME_SETTINGS: 'retro-adventure-settings',
  VOCABULARY_PROGRESS: 'retro-adventure-vocabulary',
} as const;

// Save game state to localStorage
export const saveGameState = (gameState: GameState): void => {
  try {
    const serializedState = JSON.stringify({
      ...gameState,
      timestamp: Date.now(),
    });
    localStorage.setItem(STORAGE_KEYS.GAME_STATE, serializedState);
  } catch (error) {
    console.error('Failed to save game state:', error);
  }
};

// Load game state from localStorage
export const loadGameState = (): GameState | null => {
  try {
    const serializedState = localStorage.getItem(STORAGE_KEYS.GAME_STATE);
    if (!serializedState) return null;

    const parsedState = JSON.parse(serializedState);
    
    // Validate the loaded state structure
    if (
      parsedState &&
      typeof parsedState.session_id === 'string' &&
      typeof parsedState.turn === 'number' &&
      Array.isArray(parsedState.history)
    ) {
      return parsedState;
    }
    
    return null;
  } catch (error) {
    console.error('Failed to load game state:', error);
    return null;
  }
};

// Clear game state from localStorage
export const clearGameState = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEYS.GAME_STATE);
  } catch (error) {
    console.error('Failed to clear game state:', error);
  }
};

// Save game settings
export const saveGameSettings = (settings: Record<string, any>): void => {
  try {
    const serializedSettings = JSON.stringify(settings);
    localStorage.setItem(STORAGE_KEYS.GAME_SETTINGS, serializedSettings);
  } catch (error) {
    console.error('Failed to save game settings:', error);
  }
};

// Load game settings
export const loadGameSettings = (): Record<string, any> | null => {
  try {
    const serializedSettings = localStorage.getItem(STORAGE_KEYS.GAME_SETTINGS);
    return serializedSettings ? JSON.parse(serializedSettings) : null;
  } catch (error) {
    console.error('Failed to load game settings:', error);
    return null;
  }
};

// Save vocabulary progress
export interface VocabularyProgress {
  words_learned: string[];
  definitions_viewed: string[];
  total_games_played: number;
  last_played: number;
}

export const saveVocabularyProgress = (progress: VocabularyProgress): void => {
  try {
    const serializedProgress = JSON.stringify(progress);
    localStorage.setItem(STORAGE_KEYS.VOCABULARY_PROGRESS, serializedProgress);
  } catch (error) {
    console.error('Failed to save vocabulary progress:', error);
  }
};

export const loadVocabularyProgress = (): VocabularyProgress | null => {
  try {
    const serializedProgress = localStorage.getItem(STORAGE_KEYS.VOCABULARY_PROGRESS);
    if (!serializedProgress) return null;

    const progress = JSON.parse(serializedProgress);
    
    // Validate structure
    if (
      progress &&
      Array.isArray(progress.words_learned) &&
      Array.isArray(progress.definitions_viewed) &&
      typeof progress.total_games_played === 'number'
    ) {
      return progress;
    }
    
    return null;
  } catch (error) {
    console.error('Failed to load vocabulary progress:', error);
    return null;
  }
};

// Create a backup of the current game state
export const createGameBackup = (gameState: GameState): string => {
  try {
    return JSON.stringify({
      ...gameState,
      backup_timestamp: Date.now(),
    });
  } catch (error) {
    console.error('Failed to create game backup:', error);
    return '';
  }
};

// Restore game state from backup
export const restoreFromBackup = (backup: string): GameState | null => {
  try {
    const parsedBackup = JSON.parse(backup);
    
    // Remove backup metadata
    delete parsedBackup.backup_timestamp;
    
    return parsedBackup;
  } catch (error) {
    console.error('Failed to restore from backup:', error);
    return null;
  }
};

// Check if localStorage is available
export const isStorageAvailable = (): boolean => {
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
};

// Get storage usage information
export const getStorageInfo = (): { used: number; available: boolean } => {
  if (!isStorageAvailable()) {
    return { used: 0, available: false };
  }

  let used = 0;
  try {
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        used += localStorage[key].length + key.length;
      }
    }
  } catch (error) {
    console.error('Failed to calculate storage usage:', error);
  }

  return { used, available: true };
};

// Clean up old game states (keep only the most recent)
export const cleanupOldGameStates = (): void => {
  try {
    // In a more complex app, you might keep multiple save slots
    // For now, we just ensure we're not storing duplicate data
    const currentState = loadGameState();
    if (currentState) {
      clearGameState();
      saveGameState(currentState);
    }
  } catch (error) {
    console.error('Failed to cleanup old game states:', error);
  }
};
