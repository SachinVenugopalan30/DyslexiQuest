# Session management for game state

import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from app.models.game import GameState, GameTurn, PlayerProgress
from app.core.config import settings, GAME_CONFIG

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages game sessions and their state"""
    
    def __init__(self):
        self.sessions: Dict[str, GameState] = {}
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def create_session(self, session_id: str, genre: str) -> GameState:
        """Create a new game session"""
        
        # Clean up old sessions if needed
        self._cleanup_expired_sessions()
        
        # Check session limit
        if len(self.sessions) >= settings.max_sessions:
            self._force_cleanup_oldest_sessions()
        
        # Create player progress
        player_progress = PlayerProgress(
            current_segment_id="",
            current_difficulty=2  # Default difficulty
        )
        
        # Create new game state - session_id will be auto-generated if empty
        if not session_id:
            game_state = GameState(
                genre=genre,
                player_progress=player_progress
            )
        else:
            game_state = GameState(
                session_id=session_id,
                genre=genre,
                player_progress=player_progress
            )
        
        self.sessions[game_state.session_id] = game_state
        logger.info(f"Created new session: {session_id}")
        
        return game_state
    
    def get_session(self, session_id: str) -> Optional[GameState]:
        """Get existing game session"""
        
        if session_id not in self.sessions:
            return None
        
        # Update last active timestamp
        self.sessions[session_id].last_active = datetime.now()
        
        return self.sessions[session_id]
    
    def update_session(self, session_id: str, game_state: GameState) -> bool:
        """Update existing game session"""
        
        if session_id not in self.sessions:
            logger.warning(f"Attempted to update non-existent session: {session_id}")
            return False
        
        # Update timestamp
        game_state.last_active = datetime.now()
        self.sessions[session_id] = game_state
        
        return True
    
    def add_turn(self, session_id: str, user_input: str, ai_response: str, vocabulary_words: list) -> bool:
        """Add a new turn to the game session"""
        
        game_state = self.get_session(session_id)
        if not game_state:
            return False
        
        # Create new turn
        new_turn = GameTurn(
            turn=game_state.turn + 1,
            user_input=user_input,
            ai_response=ai_response,
            vocabulary_words=vocabulary_words,
            timestamp=time.time()
        )
        
        # Update game state
        game_state.history.append(new_turn)
        game_state.turn = new_turn.turn
        
        # Add new vocabulary words
        for word in vocabulary_words:
            if word not in game_state.vocabulary_learned:
                game_state.vocabulary_learned.append(word)
        
        # Check if game should end
        if game_state.turn >= GAME_CONFIG["MAX_TURNS"]:
            game_state.game_over = True
        
        # Update session
        self.update_session(session_id, game_state)
        
        return True
    
    def backtrack_session(self, session_id: str, target_turn: int) -> Optional[GameState]:
        """Backtrack game session to a previous turn"""
        
        game_state = self.get_session(session_id)
        if not game_state:
            return None
        
        # Validate backtrack request
        if (game_state.backtrack_count >= GAME_CONFIG["MAX_BACKTRACK"] or 
            target_turn >= game_state.turn or 
            target_turn < 1):
            return None
        
        # Find the target turn in history
        target_history = []
        for turn in game_state.history:
            if turn.turn <= target_turn:
                target_history.append(turn)
            else:
                break
        
        if not target_history:
            return None
        
        # Create new game state with truncated history
        new_game_state = GameState(
            session_id=session_id,
            genre=game_state.genre,
            turn=target_turn,
            player_progress=game_state.player_progress,
            history=target_history,
            vocabulary_learned=game_state.vocabulary_learned.copy(),
            game_over=False,
            backtrack_count=game_state.backtrack_count + 1,
            session_limit=game_state.session_limit,
            adaptive_difficulty=game_state.adaptive_difficulty,
            text_to_speech_enabled=game_state.text_to_speech_enabled,
            created_at=game_state.created_at
        )
        
        # Update session
        self.update_session(session_id, new_game_state)
        
        logger.info(f"Backtracked session {session_id} to turn {target_turn}")
        
        return new_game_state
    
    def end_session(self, session_id: str) -> bool:
        """End a game session"""
        
        if session_id not in self.sessions:
            return False
        
        # Mark as game over
        self.sessions[session_id].game_over = True
        
        logger.info(f"Ended session: {session_id}")
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a game session completely"""
        
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        
        return False
    
    def get_session_count(self) -> int:
        """Get current number of active sessions"""
        return len(self.sessions)
    
    def get_session_stats(self) -> dict:
        """Get statistics about current sessions"""
        
        if not self.sessions:
            return {
                "total_sessions": 0,
                "active_games": 0,
                "completed_games": 0,
                "average_turns": 0
            }
        
        active_games = sum(1 for session in self.sessions.values() if not session.game_over)
        completed_games = sum(1 for session in self.sessions.values() if session.game_over)
        
        total_turns = sum(session.turn for session in self.sessions.values())
        average_turns = total_turns / len(self.sessions) if self.sessions else 0
        
        return {
            "total_sessions": len(self.sessions),
            "active_games": active_games,
            "completed_games": completed_games,
            "average_turns": round(average_turns, 2)
        }
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        
        current_time = time.time()
        
        # Only run cleanup periodically
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        expiry_time = datetime.now() - timedelta(seconds=GAME_CONFIG["SESSION_TIMEOUT"])
        expired_sessions = []
        
        for session_id, game_state in self.sessions.items():
            if game_state.last_active < expiry_time:
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        self.last_cleanup = current_time
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def _force_cleanup_oldest_sessions(self):
        """Force cleanup of oldest sessions when limit is reached"""
        
        if not self.sessions:
            return
        
        # Sort sessions by last active time
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].last_active
        )
        
        # Remove oldest 10% of sessions
        num_to_remove = max(1, len(sorted_sessions) // 10)
        
        for i in range(num_to_remove):
            session_id, _ = sorted_sessions[i]
            del self.sessions[session_id]
            logger.info(f"Force cleaned up session: {session_id}")
        
        logger.info(f"Force cleaned up {num_to_remove} oldest sessions")


# Global session manager instance
session_manager = SessionManager()
