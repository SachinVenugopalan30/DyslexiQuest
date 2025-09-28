# API routes for DyslexiQuest

import logging
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from app.models.game import (
    GameChoiceRequest, GameChallengeRequest, GameInteractionResponse,
    GameBacktrackRequest, GameBacktrackResponse,
    GameEndRequest, GameEndResponse, GameNextRequest, GameNextResponse,
    HealthResponse, PlayerProgress
)

from app.core.llm import gemini_client
from app.utils.session_manager import session_manager
from app.core.config import settings, GAME_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start")
async def start_game(request: dict):
    """Start a new DyslexiQuest game"""
    
    try:
        # Handle both traditional and educational request formats
        raw_genre = request.get('genre', 'fantasy')
        difficulty_level = request.get('difficulty_level', 2)
        session_limit = request.get('session_limit', 8)
        text_to_speech = request.get('text_to_speech', False)
        
        # Map incoming genre to valid GameState genre values
        genre_mapping = {
            'fantasy': 'dungeon',
            'adventure': 'forest', 
            'sci-fi': 'space',
            'mystery': 'mystery',
            'forest': 'forest',
            'space': 'space', 
            'dungeon': 'dungeon'
        }
        genre = genre_mapping.get(raw_genre, 'forest')
        
        # Create new session
        game_state = session_manager.create_session(
            session_id="",  # Will be generated in create_session
            genre=genre
        )
        
        # Import story generator
        from app.utils.story_generator import story_generator
        
        # Initialize player progress
        player_progress = PlayerProgress(
            current_segment_id="",
            current_difficulty=difficulty_level
        )
        
        # Update game state for educational mode
        game_state.player_progress = player_progress
        game_state.session_limit = session_limit
        game_state.text_to_speech_enabled = text_to_speech
        game_state.adaptive_difficulty = True
        
        # Generate first story segment using dynamic LLM generation
        try:            
            # Create a new unique story beginning - use the mapped genre directly
            first_segment = await gemini_client.generate_new_story_beginning(genre)
        except Exception as e:
            logger.error(f"Failed to generate dynamic story beginning: {e}")
            # Fall back to template generation
            first_segment = story_generator.generate_segment(
                genre=raw_genre,  # Use original genre for fallback compatibility
                difficulty=difficulty_level,
                segment_index=0
            )
        
        # Ensure we have a StorySegment object
        if isinstance(first_segment, dict):
            # Convert dict to StorySegment - this should not happen with the new system
            logger.warning("Received dict instead of StorySegment, falling back to template generation")
            first_segment = story_generator.generate_segment(
                genre=raw_genre,
                difficulty=difficulty_level,
                segment_index=0
            )
        
        game_state.story_segments.append(first_segment)
        game_state.player_progress.current_segment_id = first_segment.id
        game_state.turn = 1
        
        # Update session
        session_manager.update_session(game_state.session_id, game_state)
        
        logger.info(f"Started new {genre} educational game: {game_state.session_id}")
        
        # Extract choices from the first segment
        choices = []
        if first_segment.multiple_choices:
            choices = [f"{i+1}. {choice.text}" for i, choice in enumerate(first_segment.multiple_choices)]
        
        # Return format compatible with traditional frontend
        return {
            "session_id": game_state.session_id,
            "story_intro": first_segment.text,
            "turn": game_state.turn,
            "choices": choices
        }
        
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        raise HTTPException(status_code=500, detail="Failed to start game")


@router.post("/choice", response_model=GameInteractionResponse)
async def handle_choice(request: GameChoiceRequest) -> GameInteractionResponse:
    """Handle player's multiple choice selection"""
    
    try:
        # Get game state
        game_state = session_manager.get_session(request.session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        if game_state.game_over:
            raise HTTPException(status_code=400, detail="Game already completed")
        
        # Find current segment
        current_segment = None
        for segment in game_state.story_segments:
            if segment.id == request.segment_id:
                current_segment = segment
                break
        
        if not current_segment:
            raise HTTPException(status_code=404, detail="Story segment not found")
        
        # Find selected choice
        selected_choice = None
        for choice in current_segment.multiple_choices:
            if choice.id == request.choice_id:
                selected_choice = choice
                break
        
        if not selected_choice:
            raise HTTPException(status_code=400, detail="Invalid choice selected")
        
        # Process the choice
        from app.utils.story_generator import story_generator
        
        is_correct = selected_choice.is_correct
        feedback = selected_choice.feedback
        
        # Update player progress
        if is_correct:
            game_state.player_progress.correct_choices += 1
            reward = None
        else:
            game_state.player_progress.incorrect_choices += 1
            reward = None
        
        # Generate next segment or provide hint
        next_segment = None
        session_complete = False
        
        if is_correct:
            # Move to next segment if not at turn limit (stories should always go to 15 turns)
            if game_state.turn < GAME_CONFIG["MAX_TURNS"] - 1:
                # Collect previous choices and story context for LLM
                previous_choices = [turn.user_input for turn in game_state.history[-3:] if turn.user_input]
                story_context = [segment.text for segment in game_state.story_segments[-2:]] if game_state.story_segments else []
                
                # Map genre to adventure category for dynamic generation
                genre_mapping = {
                    'fantasy': 'dungeon',
                    'adventure': 'forest', 
                    'sci-fi': 'space',
                    'mystery': 'mystery',
                    'space': 'space',  # Add direct mapping for space
                    'forest': 'forest',  # Add direct mapping for forest
                    'dungeon': 'dungeon',  # Add direct mapping for dungeon
                }
                adventure_category = genre_mapping.get(game_state.genre, 'forest')
                logger.info(f"Genre mapping: {game_state.genre} -> {adventure_category}")
                
                # Create adventure info for the theme
                adventure_info = {
                    'name': f'{adventure_category.title()} Adventure',
                    'description': f'An exciting {adventure_category} adventure',
                    'themes': [],
                    'vocabulary_focus': []
                }
                
                try:
                    next_segment = await gemini_client.generate_story_segment(
                        segment_number=len(game_state.story_segments) + 1,
                        adventure_category=adventure_category,
                        adventure_info=adventure_info,
                        previous_choices=previous_choices,
                        story_context=story_context
                    )
                except Exception as e:
                    logger.error(f"Failed to generate dynamic story segment: {e}")
                    # Fall back to template generation
                    next_segment = story_generator.generate_segment(
                        genre=game_state.genre,
                        difficulty=game_state.player_progress.current_difficulty,
                        segment_index=len(game_state.story_segments)
                    )
                
                game_state.story_segments.append(next_segment)
                game_state.player_progress.current_segment_id = next_segment.id
                game_state.current_segment_index += 1
            else:
                session_complete = True
                game_state.game_over = True
                reward = None
        
        # Add turn to history
        from app.models.game import GameTurn
        turn = GameTurn(
            turn=game_state.turn + 1,
            segment=current_segment,
            player_choice=request.choice_id,  # Store choice ID for internal use
            user_input=selected_choice.text,  # Store the actual choice text for frontend display
            was_correct=is_correct,
            reward_earned=reward,
            timestamp=time.time()
        )
        
        game_state.history.append(turn)
        game_state.turn += 1
        
        # Update session
        session_manager.update_session(request.session_id, game_state)
        
        return GameInteractionResponse(
            is_correct=is_correct,
            feedback=feedback,
            hint=None,
            reward_earned=reward,
            next_segment=next_segment,
            player_progress=game_state.player_progress,
            game_over=game_state.game_over,
            session_complete=session_complete
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling choice: {e}")
        raise HTTPException(status_code=500, detail="Failed to process choice")


@router.post("/challenge", response_model=GameInteractionResponse)
async def handle_challenge(request: GameChallengeRequest) -> GameInteractionResponse:
    """Handle player's word challenge response"""
    
    try:
        # Get game state
        game_state = session_manager.get_session(request.session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        # Find current segment
        current_segment = None
        for segment in game_state.story_segments:
            if segment.id == request.segment_id:
                current_segment = segment
                break
        
        if not current_segment or not current_segment.word_challenge:
            raise HTTPException(status_code=404, detail="Word challenge not found")
        
        challenge = current_segment.word_challenge
        is_correct = request.challenge_response.lower().strip() == challenge.correct_answer.lower().strip()
        
        # Process challenge result
        if is_correct:
            feedback = "Correct."
            reward = None
            game_state.player_progress.challenges_completed += 1
        else:
            feedback = f"Incorrect. {challenge.hint}"
            reward = None
        
        # Update session
        session_manager.update_session(request.session_id, game_state)
        
        return GameInteractionResponse(
            is_correct=is_correct,
            feedback=feedback,
            hint=challenge.hint if not is_correct else None,
            reward_earned=reward,
            next_segment=None,  # Challenges don't advance segments
            player_progress=game_state.player_progress,
            game_over=False,
            session_complete=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to process challenge")
@router.post("/backtrack", response_model=GameBacktrackResponse)
async def backtrack_game(request: GameBacktrackRequest) -> GameBacktrackResponse:
    """Backtrack to a previous turn"""
    
    try:
        # Get game session
        game_state = session_manager.get_session(request.session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        # Validate backtrack request
        if game_state.backtrack_count >= GAME_CONFIG["MAX_BACKTRACK"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum backtrack limit ({GAME_CONFIG['MAX_BACKTRACK']}) reached"
            )
        
        if request.target_turn >= game_state.turn:
            raise HTTPException(status_code=400, detail="Cannot backtrack to current or future turn")
        
        if request.target_turn < 1:
            raise HTTPException(status_code=400, detail="Invalid target turn")
        
        # Perform backtrack
        restored_state = session_manager.backtrack_session(
            session_id=request.session_id,
            target_turn=request.target_turn
        )
        
        if not restored_state:
            raise HTTPException(status_code=400, detail="Failed to backtrack")
        
        # Generate backtrack message
        message = f"Returned to turn {request.target_turn}."
        
        logger.info(f"Backtracked session {request.session_id} to turn {request.target_turn}")
        
        return GameBacktrackResponse(
            restored_state=restored_state,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error backtracking game: {e}")
        raise HTTPException(status_code=500, detail="Failed to backtrack")


@router.post("/end", response_model=GameEndResponse)
async def end_game(request: GameEndRequest) -> GameEndResponse:
    """End the current game"""
    
    try:
        # Get game session
        game_state = session_manager.get_session(request.session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        # End the session
        success = session_manager.end_session(request.session_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to end game")
        
        logger.info(f"Ended game session: {request.session_id}")
        
        return GameEndResponse(
            message="Game ended."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending game: {e}")
        raise HTTPException(status_code=500, detail="Failed to end game")


@router.post("/next", response_model=GameNextResponse)
async def next_turn(request: GameNextRequest) -> GameNextResponse:
    """Handle next turn in traditional text adventure format (compatibility endpoint)"""
    
    try:
        # Get game state
        game_state = session_manager.get_session(request.session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        if game_state.game_over:
            raise HTTPException(status_code=400, detail="Game already completed")
        
        # Get current segment
        if not game_state.story_segments:
            raise HTTPException(status_code=400, detail="No story segments found")
        
        current_segment = game_state.story_segments[-1]
        
        # Dynamic choice mapping - extract choice number from user input
        choice_id = 0  # Default to first choice
        user_input_lower = request.user_input.lower().strip()
        
        # Extract number from input like "1. Follow the butterfly 🦋" -> 0 (0-indexed)
        if user_input_lower.startswith(("1.", "1 ")):
            choice_id = 0
        elif user_input_lower.startswith(("2.", "2 ")):
            choice_id = 1
        elif user_input_lower.startswith(("3.", "3 ")):
            choice_id = 2
        elif user_input_lower.startswith(("4.", "4 ")):
            choice_id = 3
        
        # Use the choice endpoint logic
        from app.utils.story_generator import story_generator
        
        if choice_id < len(current_segment.multiple_choices):
            selected_choice = current_segment.multiple_choices[choice_id]
            is_correct = selected_choice.is_correct
        else:
            # Default to first choice if mapping fails
            selected_choice = current_segment.multiple_choices[0]
            is_correct = True
        
        # Process the choice - all choices are valid story paths
        game_state.player_progress.correct_choices += 1  # Track all choices as progress
        reward = None
        
        # Generate feedback for the choice
        choice_feedback = f"{selected_choice.feedback}" if selected_choice.feedback else ""
        
        # Generate next segment or end game based on turn limit
        next_segment = None
        session_complete = False
        
        # Continue story unless we've reached the turn limit
        if game_state.turn < GAME_CONFIG["MAX_TURNS"] - 1:
            # Collect previous choices and story context for LLM
            previous_choices = [turn.user_input for turn in game_state.history[-3:] if turn.user_input]
            previous_choices.append(request.user_input)  # Add current choice for context
            story_context = [segment.text for segment in game_state.story_segments[-2:]] if game_state.story_segments else []
            
            # Map genre to adventure category for dynamic generation
            genre_mapping = {
                'fantasy': 'dungeon',
                'adventure': 'forest', 
                'sci-fi': 'space',
                'mystery': 'mystery',
                'space': 'space',  # Add direct mapping for space
                'forest': 'forest',  # Add direct mapping for forest
                'dungeon': 'dungeon',  # Add direct mapping for dungeon
            }
            adventure_category = genre_mapping.get(game_state.genre, 'forest')
            logger.info(f"Genre mapping in /next: {game_state.genre} -> {adventure_category}")
            
            # Create adventure info for the theme
            adventure_info = {
                'name': f'{adventure_category.title()} Adventure',
                'description': f'An exciting {adventure_category} adventure',
                'themes': [],
                'vocabulary_focus': []
            }
            
            try:
                next_segment = await gemini_client.generate_story_segment(
                    segment_number=len(game_state.story_segments) + 1,
                    adventure_category=adventure_category,
                    adventure_info=adventure_info,
                    previous_choices=previous_choices,
                    story_context=story_context
                )
            except Exception as e:
                logger.error(f"Failed to generate dynamic story segment: {e}")
                next_segment = story_generator.generate_segment(
                    genre=game_state.genre,
                    difficulty=game_state.player_progress.current_difficulty,
                    segment_index=len(game_state.story_segments)
                )
            
            game_state.story_segments.append(next_segment)
            game_state.player_progress.current_segment_id = next_segment.id
            game_state.current_segment_index += 1
        elif game_state.turn >= GAME_CONFIG["MAX_TURNS"] - 1:
            session_complete = True
            game_state.game_over = True
            reward = None
        
        # Add turn to history
        from app.models.game import GameTurn
        turn = GameTurn(
            turn=game_state.turn + 1,
            segment=current_segment,
            player_choice=request.user_input,  # Store user input for internal use
            user_input=request.user_input,  # Store the same for frontend display
            was_correct=is_correct,
            reward_earned=reward,
            timestamp=time.time()
        )
        
        game_state.history.append(turn)
        game_state.turn += 1
        
        # Update session
        session_manager.update_session(request.session_id, game_state)
        
        # Format response for traditional game frontend
        if next_segment:
            # Combine choice feedback with new story segment
            response_text = f"{choice_feedback}\n\n{next_segment.text}" if choice_feedback else next_segment.text
        elif session_complete:
            response_text = "Adventure complete."
        else:
            # End of game due to turn limit
            response_text = f"{choice_feedback}\n\nAdventure complete." if choice_feedback else "Adventure complete."
            game_state.game_over = True
        
        # Convert to traditional GameNextResponse format
        vocabulary_words = []
        if next_segment and next_segment.vocabulary_words:
            vocabulary_words = next_segment.vocabulary_words
        
        # Extract choices from the next segment
        choices = []
        if next_segment and next_segment.multiple_choices and not game_state.game_over:
            choices = [f"{i+1}. {choice.text}" for i, choice in enumerate(next_segment.multiple_choices)]
        
        return GameNextResponse(
            response=response_text,
            turn=game_state.turn,
            vocabulary_words=vocabulary_words,
            game_over=game_state.game_over,
            choices=choices
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in next turn: {e}")
        raise HTTPException(status_code=500, detail="Failed to process next turn")


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API and Gemini health status"""
    
    try:
        # Check Gemini availability
        gemini_available = await gemini_client.check_health()
        
        # Determine overall status
        status = "healthy" if gemini_available else "degraded"
        
        # Get session statistics
        session_stats = session_manager.get_session_stats()
        
        logger.info(f"Health check: {status}, Gemini: {gemini_available}, Sessions: {session_stats['total_sessions']}")
        
        return HealthResponse(
            status=status,
            gemini_available=gemini_available
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="degraded",
            gemini_available=False
        )


# Background task to clean up sessions
async def cleanup_sessions():
    """Background task to clean up expired sessions"""
    try:
        session_manager._cleanup_expired_sessions()
        logger.debug("Session cleanup completed")
    except Exception as e:
        logger.error(f"Session cleanup error: {e}")


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get API statistics (for monitoring)"""
    
    try:
        session_stats = session_manager.get_session_stats()
        gemini_status = await gemini_client.check_health()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sessions": session_stats,
            "gemini_available": gemini_status,
            "api_version": "1.0.0",
            "max_sessions": settings.max_sessions,
            "max_turns": GAME_CONFIG["MAX_TURNS"],
            "max_backtrack": GAME_CONFIG["MAX_BACKTRACK"]
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
