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
    """Start a new DyslexiQuest educational game with progressive learning"""
    
    try:
        # Handle both traditional and educational request formats
        raw_genre = request.get('genre', 'forest')

        progressive_mode = request.get('progressive_mode', True)  # Enable progressive learning
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
        
        # Initialize player progress for children
        player_progress = PlayerProgress(
            current_segment_id="",
            current_difficulty=1  # Always start easy for children
        )
        
        # Update game state for progressive educational mode
        game_state.player_progress = player_progress
        game_state.session_limit = 7  # Fixed 7 rounds for progressive learning
        game_state.text_to_speech_enabled = text_to_speech
        game_state.adaptive_difficulty = True
        game_state.progressive_mode = progressive_mode
        game_state.current_round = 1
        
        # Generate first educational round (Round 1 - Easy difficulty)
        try:
            if progressive_mode:
                first_segment = await story_generator.generate_educational_round(
                    round_number=1,
                    theme=genre
                )
            else:
                # Fall back to traditional story generation
                first_segment = await gemini_client.generate_new_story_beginning(genre)
        except Exception as e:
            logger.error(f"Failed to generate educational round: {e}")
            # Fall back to template generation
            first_segment = story_generator.generate_segment(
                genre=raw_genre,
                difficulty=1,  # Start easy
                segment_index=0
            )
        
        # Ensure we have a StorySegment object
        if isinstance(first_segment, dict):
            logger.warning("Received dict instead of StorySegment, falling back to template generation")
            first_segment = story_generator.generate_segment(
                genre=raw_genre,
                difficulty=1,
                segment_index=0
            )
        
        game_state.story_segments.append(first_segment)
        game_state.player_progress.current_segment_id = first_segment.id
        game_state.turn = 1
        
        # Update session
        session_manager.update_session(game_state.session_id, game_state)
        
        logger.info(f"Started new {genre} educational game (Round 1): {game_state.session_id}")
        
        # Extract choices from the first segment for display
        choices = []
        if first_segment.multiple_choices:
            choices = [choice.text for choice in first_segment.multiple_choices]
        
        # Enable progressive mode for child-friendly learning
        progressive_mode = True
        
        # Return format compatible with traditional frontend  
        return {
            "session_id": game_state.session_id,
            "story_intro": first_segment.text,
            "question": first_segment.question or "What do you want to do next?",
            "turn": game_state.turn,
            "choices": choices,
            "round": 1,
            "difficulty": "easy",
            "progressive_mode": progressive_mode
        }
        
    except Exception as e:
        logger.error(f"Error starting educational game: {e}")
        raise HTTPException(status_code=500, detail="Failed to start educational game")


@router.post("/choice", response_model=GameInteractionResponse)
async def handle_choice(request: GameChoiceRequest) -> GameInteractionResponse:
    """Handle player's multiple choice selection in progressive learning mode"""
    
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
        
        # Process the choice for progressive learning system
        from app.utils.story_generator import story_generator
        
        is_correct = selected_choice.is_correct
        feedback = selected_choice.feedback
        hint = None
        
        # Generate helpful hints for wrong answers (child-friendly)
        if not is_correct and game_state.progressive_mode:
            try:
                # Find the correct answer text
                correct_choice = None
                for choice in current_segment.multiple_choices:
                    if choice.is_correct:
                        correct_choice = choice
                        break
                
                if correct_choice:
                    hint = await gemini_client.generate_hint_for_wrong_answer(
                        question=current_segment.text,
                        correct_answer=correct_choice.text,
                        wrong_answer=selected_choice.text,
                        theme=game_state.genre
                    )
                else:
                    hint = "Try again! 🌟 Think carefully about the question."
            except Exception as e:
                logger.error(f"Failed to generate hint: {e}")
                hint = "Good try! 🤔 Look at the story again for clues."
        
        # Update player progress
        if is_correct:
            game_state.player_progress.correct_choices += 1
            feedback = "Great job! 🌟 You got it right!"
            
            # Award points or rewards for correct answers
            from app.models.game import Reward
            reward = Reward(
                type='star',
                name='Correct Answer',
                description='You picked the right answer!',
                icon='⭐',
                points=10
            )
        else:
            game_state.player_progress.incorrect_choices += 1
            feedback = "Not quite right. Try again! 😊"
            reward = None
        
        # Generate next educational round if correct answer
        next_segment = None
        session_complete = False
        current_difficulty = "easy" if game_state.current_round <= 2 else "intermediate" if game_state.current_round <= 5 else "difficult"
        
        if is_correct and game_state.progressive_mode:
            # Move to next round (1-7 total rounds)
            if game_state.current_round < 7:
                next_round = game_state.current_round + 1
                
                try:
                    next_segment = await story_generator.generate_educational_round(
                        round_number=next_round,
                        theme=game_state.genre
                    )
                    
                    game_state.story_segments.append(next_segment)
                    game_state.player_progress.current_segment_id = next_segment.id
                    game_state.current_round = next_round
                    game_state.current_segment_index += 1
                    
                except Exception as e:
                    logger.error(f"Failed to generate next educational round: {e}")
                    # Mark session as complete if we can't generate more content
                    session_complete = True
                    game_state.game_over = True
            else:
                # Completed all 7 rounds!
                session_complete = True
                game_state.game_over = True
                feedback = "Amazing work! 🎉 You completed all 7 learning rounds!"
                
                # Special completion reward
                reward = Reward(
                    type='achievement',
                    name='Learning Champion',
                    description='You completed all educational rounds!',
                    icon='👑',
                    points=100
                )
        
        # Add turn to history
        from app.models.game import GameTurn
        turn = GameTurn(
            turn=game_state.turn + 1,
            segment=current_segment,
            player_choice=request.choice_id,
            user_input=selected_choice.text,
            was_correct=is_correct,
            hint_given=hint is not None,
            reward_earned=reward,
            timestamp=time.time()
        )
        
        game_state.history.append(turn)
        game_state.turn += 1
        
        # Store hint for this segment if provided
        if hint:
            game_state.hints_shown[current_segment.id] = hint
        
        # Update session
        session_manager.update_session(request.session_id, game_state)
        
        return GameInteractionResponse(
            is_correct=is_correct,
            feedback=feedback,
            hint=hint,
            reward_earned=reward,
            next_segment=next_segment,
            player_progress=game_state.player_progress,
            game_over=game_state.game_over,
            session_complete=session_complete,
            current_round=game_state.current_round,
            difficulty_level=current_difficulty
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling choice in educational mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to process educational choice")


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
        
        # Dynamic choice mapping - match user input to actual choice text
        choice_id = 0  # Default to first choice
        user_input_lower = request.user_input.lower().strip()
        
        # First try to match by number prefix (like "1.", "2.", etc.)
        if user_input_lower.startswith(("1.", "1 ")):
            choice_id = 0
        elif user_input_lower.startswith(("2.", "2 ")):
            choice_id = 1
        elif user_input_lower.startswith(("3.", "3 ")):
            choice_id = 2
        elif user_input_lower.startswith(("4.", "4 ")):
            choice_id = 3
        else:
            # If no number prefix, match by actual choice text content
            for i, choice in enumerate(current_segment.multiple_choices):
                choice_text_clean = choice.text.lower().strip()
                # Remove common prefixes and suffixes to get core text
                if choice_text_clean.startswith(("1.", "2.", "3.", "4.")):
                    choice_text_clean = choice_text_clean[2:].strip()
                
                # Check if user input matches the choice text (exact or contains)
                if (user_input_lower == choice_text_clean or 
                    choice_text_clean in user_input_lower or 
                    user_input_lower in choice_text_clean):
                    choice_id = i
                    break
        
        # Use the choice endpoint logic
        from app.utils.story_generator import story_generator
        
        # Debug: Log the user input and choice mapping
        logger.info(f"User input: '{request.user_input}', mapped to choice_id: {choice_id}")
        logger.info(f"Available choices: {[(i, choice.text, choice.is_correct) for i, choice in enumerate(current_segment.multiple_choices)]}")
        
        # Additional debug: Log the selected choice details
        if choice_id < len(current_segment.multiple_choices):
            selected = current_segment.multiple_choices[choice_id]
            logger.info(f"Selected choice {choice_id}: text='{selected.text}', is_correct={selected.is_correct}")
        
        if choice_id < len(current_segment.multiple_choices):
            selected_choice = current_segment.multiple_choices[choice_id]
            is_correct = selected_choice.is_correct
        else:
            # Default to first choice if mapping fails
            selected_choice = current_segment.multiple_choices[0]
            is_correct = False  # Default to incorrect for educational mode
            logger.warning(f"Choice mapping failed, defaulting to first choice")
        
        # In progressive mode, check if answer is correct
        if game_state.progressive_mode and not is_correct:
            # Wrong answer - provide feedback and don't advance
            hint = selected_choice.feedback or "Try again! 🤔 Look at the story carefully."
            
            # Generate a helpful hint using LLM
            try:
                correct_choice = None
                for choice in current_segment.multiple_choices:
                    if choice.is_correct:
                        correct_choice = choice
                        break
                
                if correct_choice:
                    hint = await gemini_client.generate_hint_for_wrong_answer(
                        question=getattr(current_segment, 'question', current_segment.text),
                        correct_answer=correct_choice.text,
                        wrong_answer=selected_choice.text,
                        theme=game_state.genre
                    )
            except Exception as e:
                logger.error(f"Failed to generate hint: {e}")
                hint = "Good try! 🤔 Read the story again and think about what really happened."
            
            # Don't increment turn count for wrong answers
            response_text = f"❌ {hint}\n\nTry picking another answer!"
            
            # Extract choices for retry (same segment)
            choices = []
            if current_segment.multiple_choices:
                choices = [f"{i+1}. {choice.text}" for i, choice in enumerate(current_segment.multiple_choices)]
            
            return GameNextResponse(
                response=response_text,
                turn=game_state.turn,  # Don't increment turn
                vocabulary_words=current_segment.vocabulary_words or [],
                game_over=False,
                choices=choices,
                question=getattr(current_segment, 'question', "What do you want to do next?")
            )
        
        # Correct answer or traditional mode
        if is_correct and game_state.progressive_mode:
            game_state.player_progress.correct_choices += 1
            choice_feedback = "✅ Great job! 🌟 You got it right!"
        else:
            # Traditional mode - all choices valid
            game_state.player_progress.correct_choices += 1
            choice_feedback = selected_choice.feedback if selected_choice.feedback else ""
        
        reward = None
        
        # Generate next segment or end game based on turn limit
        next_segment = None
        session_complete = False
        
        # Only generate next round if answer was correct (in progressive mode) or if traditional mode
        should_advance = (not game_state.progressive_mode) or is_correct
        
        # For progressive mode, check 7-round limit; for traditional mode, use MAX_TURNS
        turn_limit = 7 if game_state.progressive_mode else GAME_CONFIG["MAX_TURNS"] - 1
        
        # Continue story unless we've reached the appropriate turn limit
        if should_advance and game_state.current_round < turn_limit:
            if game_state.progressive_mode:
                # Generate next educational round (2-7)
                next_round = game_state.current_round + 1
                try:
                    next_segment = await story_generator.generate_educational_round(
                        round_number=next_round,
                        theme=game_state.genre
                    )
                    game_state.current_round = next_round
                except Exception as e:
                    logger.error(f"Failed to generate educational round {next_round}: {e}")
                    # End session if we can't generate next round
                    session_complete = True
                    game_state.game_over = True
            else:
                # Traditional story mode
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
            
            if next_segment:
                game_state.story_segments.append(next_segment)
                game_state.player_progress.current_segment_id = next_segment.id
                game_state.current_segment_index += 1
        elif (game_state.progressive_mode and game_state.current_round >= 7) or (not game_state.progressive_mode and game_state.turn >= GAME_CONFIG["MAX_TURNS"] - 1):
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
        question = "What do you want to do next?"  # Default question
        if next_segment and next_segment.multiple_choices and not game_state.game_over:
            choices = [f"{i+1}. {choice.text}" for i, choice in enumerate(next_segment.multiple_choices)]
            # Extract the question from the segment if available
            if next_segment.question:
                question = next_segment.question
        
        return GameNextResponse(
            response=response_text,
            turn=game_state.turn,
            vocabulary_words=vocabulary_words,
            game_over=game_state.game_over,
            choices=choices,
            question=question
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
