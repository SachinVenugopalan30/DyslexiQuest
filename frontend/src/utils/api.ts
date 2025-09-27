// Types for API communication
export interface GameStartRequest {
  genre: 'forest' | 'space' | 'dungeon' | 'mystery';
}

export interface GameStartResponse {
  session_id: string;
  story_intro: string;
  turn: number;
  choices?: string[];
}

export interface GameNextRequest {
  session_id: string;
  user_input: string;
  turn: number;
}

export interface GameNextResponse {
  response: string;
  turn: number;
  vocabulary_words: string[];
  game_over: boolean;
  choices?: string[];
}

export interface GameBacktrackRequest {
  session_id: string;
  target_turn: number;
}

export interface GameBacktrackResponse {
  restored_state: GameState;
  message: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  gemini_available: boolean;
}

export interface GameState {
  session_id: string;
  turn: number;
  genre: string;
  history: GameTurn[];
  vocabulary_learned: string[];
  game_over: boolean;
  backtrack_count: number;
  current_choices?: string[];
}

export interface GameTurn {
  turn: number;
  user_input: string;
  ai_response: string;
  vocabulary_words: string[];
  timestamp: number;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API client with error handling and retry logic
class APIClient {
  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async startGame(genre: GameStartRequest['genre']): Promise<GameStartResponse> {
    return this.request<GameStartResponse>('/api/start', {
      method: 'POST',
      body: JSON.stringify({ genre }),
    });
  }

  async nextTurn(data: GameNextRequest): Promise<GameNextResponse> {
    return this.request<GameNextResponse>('/api/next', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async backtrackGame(data: GameBacktrackRequest): Promise<GameBacktrackResponse> {
    return this.request<GameBacktrackResponse>('/api/backtrack', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async endGame(session_id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('/api/end', {
      method: 'POST',
      body: JSON.stringify({ session_id }),
    });
  }

  async checkHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/api/health');
  }
}

// Singleton API client instance
export const apiClient = new APIClient();

// Utility function to handle API errors with user-friendly messages
export const handleAPIError = (error: unknown): string => {
  if (error instanceof Error) {
    if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
      return 'Unable to connect to the game server. Please check your internet connection and try again.';
    }
    if (error.message.includes('HTTP 429')) {
      return 'Too many requests. Please wait a moment and try again.';
    }
    if (error.message.includes('HTTP 5')) {
      return 'The game server is experiencing issues. Please try again in a few moments.';
    }
    return error.message;
  }
  return 'An unexpected error occurred. Please try again.';
};

// Retry wrapper for API calls
export const withRetry = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
    }
  }
  throw new Error('Max retries exceeded');
};
