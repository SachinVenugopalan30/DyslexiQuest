import { useState, useEffect, useCallback } from 'react';
import { apiClient, GameState, GameTurn, handleAPIError, withRetry } from '../utils/api';
import { saveGameState, loadGameState, clearGameState } from '../utils/localStorage';
import { announceToScreenReader } from '../utils/accessibility';
import { VocabularyManager } from '../utils/vocabulary';

export interface UseGameStateReturn {
  // Game state
  gameState: GameState | null;
  isLoading: boolean;
  error: string | null;
  isGameStarted: boolean;
  
  // Actions
  startGame: (genre: 'forest' | 'space' | 'dungeon' | 'mystery') => Promise<void>;
  sendInput: (input: string) => Promise<void>;
  backtrackToTurn: (turn: number) => Promise<void>;
  endGame: () => Promise<void>;
  newGame: () => void;
  
  // Utility
  clearError: () => void;
  vocabularyManager: VocabularyManager;
}

const MAX_BACKTRACK_COUNT = 2;
const MAX_TURNS = 15;

export const useGameState = (): UseGameStateReturn => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [vocabularyManager] = useState(() => new VocabularyManager());

  // Load saved game state on mount
  useEffect(() => {
    const savedState = loadGameState();
    if (savedState) {
      setGameState(savedState);
      announceToScreenReader('Previous game loaded successfully.');
    }
  }, []);

  // Save game state whenever it changes
  useEffect(() => {
    if (gameState) {
      saveGameState(gameState);
    }
  }, [gameState]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const startGame = useCallback(async (genre: 'forest' | 'space' | 'dungeon' | 'mystery') => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await withRetry(() => apiClient.startGame(genre));
      
      const newGameState: GameState = {
        session_id: response.session_id,
        turn: response.turn,
        genre,
        history: [{
          turn: response.turn,
          user_input: '',
          ai_response: response.story_intro,
          vocabulary_words: [],
          timestamp: Date.now(),
        }],
        vocabulary_learned: [],
        game_over: false,
        backtrack_count: 0,
        current_choices: response.choices || [
          "1. Continue exploring ✨",
          "2. Look around carefully 👀", 
          "3. Move forward slowly 👣",
          "4. Stay where you are 🛑"
        ],
      };

      setGameState(newGameState);
      announceToScreenReader(`New ${genre} adventure started! ${response.story_intro}`);
    } catch (err) {
      const errorMessage = handleAPIError(err);
      setError(errorMessage);
      announceToScreenReader(`Error starting game: ${errorMessage}`, 'assertive');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendInput = useCallback(async (input: string) => {
    if (!gameState || gameState.game_over) {
      setError('No active game session.');
      return;
    }

    if (gameState.turn >= MAX_TURNS) {
      setError('Game has reached maximum turns.');
      return;
    }

    const trimmedInput = input.trim();
    if (!trimmedInput) {
      setError('Please enter a valid response.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await withRetry(() => apiClient.nextTurn({
        session_id: gameState.session_id,
        user_input: trimmedInput,
        turn: gameState.turn,
      }));

      const newTurn: GameTurn = {
        turn: response.turn,
        user_input: trimmedInput,
        ai_response: response.response,
        vocabulary_words: response.vocabulary_words,
        timestamp: Date.now(),
      };

      // Update vocabulary learning
      response.vocabulary_words.forEach(word => {
        vocabularyManager.addLearnedWord(word);
      });

      const updatedGameState: GameState = {
        ...gameState,
        turn: response.turn,
        history: [...gameState.history, newTurn],
        vocabulary_learned: [
          ...gameState.vocabulary_learned,
          ...response.vocabulary_words.filter(
            word => !gameState.vocabulary_learned.includes(word)
          )
        ],
        game_over: response.game_over || response.turn >= MAX_TURNS,
        current_choices: response.choices || [
          "1. Continue exploring ✨",
          "2. Look around carefully 👀", 
          "3. Move forward slowly 👣",
          "4. Stay where you are 🛑"
        ],
      };

      setGameState(updatedGameState);

      // Announce new content to screen readers
      const announcement = response.game_over 
        ? `Game completed! ${response.response}` 
        : response.response;
      announceToScreenReader(announcement);

      if (response.vocabulary_words.length > 0) {
        announceToScreenReader(
          `New vocabulary words: ${response.vocabulary_words.join(', ')}`
        );
      }

    } catch (err) {
      const errorMessage = handleAPIError(err);
      setError(errorMessage);
      announceToScreenReader(`Error processing input: ${errorMessage}`, 'assertive');
    } finally {
      setIsLoading(false);
    }
  }, [gameState, vocabularyManager]);

  const backtrackToTurn = useCallback(async (targetTurn: number) => {
    if (!gameState) {
      setError('No active game session.');
      return;
    }

    if (gameState.backtrack_count >= MAX_BACKTRACK_COUNT) {
      setError('You have used all available backtracks for this game.');
      return;
    }

    if (targetTurn >= gameState.turn || targetTurn < 1) {
      setError('Invalid turn number for backtracking.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await withRetry(() => apiClient.backtrackGame({
        session_id: gameState.session_id,
        target_turn: targetTurn,
      }));

      const updatedGameState: GameState = {
        ...response.restored_state,
        backtrack_count: gameState.backtrack_count + 1,
      };

      setGameState(updatedGameState);
      announceToScreenReader(`Backtracked to turn ${targetTurn}. ${response.message}`);

    } catch (err) {
      const errorMessage = handleAPIError(err);
      setError(errorMessage);
      announceToScreenReader(`Error backtracking: ${errorMessage}`, 'assertive');
    } finally {
      setIsLoading(false);
    }
  }, [gameState]);

  const endGame = useCallback(async () => {
    if (!gameState) return;

    setIsLoading(true);
    setError(null);

    try {
      await withRetry(() => apiClient.endGame(gameState.session_id));

      const finalGameState: GameState = {
        ...gameState,
        game_over: true,
      };

      setGameState(finalGameState);
      
      // Update vocabulary manager with final progress
      vocabularyManager.updateProgress({
        total_games_played: vocabularyManager.getProgress().total_games_played + 1,
        last_played: Date.now(),
      });

      announceToScreenReader('Game ended successfully. Thank you for playing!');

    } catch (err) {
      const errorMessage = handleAPIError(err);
      setError(errorMessage);
      announceToScreenReader(`Error ending game: ${errorMessage}`, 'assertive');
    } finally {
      setIsLoading(false);
    }
  }, [gameState, vocabularyManager]);

  const newGame = useCallback(() => {
    clearGameState();
    setGameState(null);
    setError(null);
    
    // Reset vocabulary streak for new game
    vocabularyManager.resetCurrentStreak();
    
    announceToScreenReader('Ready to start a new adventure!');
  }, [vocabularyManager]);

  return {
    gameState,
    isLoading,
    error,
    isGameStarted: gameState !== null,
    startGame,
    sendInput,
    backtrackToTurn,
    endGame,
    newGame,
    clearError,
    vocabularyManager,
  };
};
