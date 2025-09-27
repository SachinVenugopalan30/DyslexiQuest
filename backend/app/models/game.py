# Backend models for educational text adventure game with dyslexia support

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
import uuid


class VisualCue(BaseModel):
    """Visual cue to support word recognition"""
    icon: str  # Unicode emoji or icon name
    description: str
    position: Literal['before', 'after', 'inline']


class MultipleChoice(BaseModel):
    """Multiple choice option for story segments"""
    id: str
    text: str
    is_correct: bool
    feedback: str  # Positive feedback for correct, gentle hint for incorrect
    visual_cue: Optional[VisualCue] = None
    difficulty_adjustment: int = 0  # -1 for easier path, 0 for same, +1 for harder


class WordChallenge(BaseModel):
    """Mini word challenge within story segments"""
    type: Literal['completion', 'matching', 'spelling', 'rhyme']
    instruction: str
    word: str
    options: List[str] = []  # For matching/multiple choice
    correct_answer: str
    hint: str
    visual_cue: Optional[VisualCue] = None
    difficulty_level: int = Field(ge=1, le=5)


class Reward(BaseModel):
    """Reward earned by player"""
    type: Literal['star', 'coin', 'badge', 'achievement']
    name: str
    description: str
    icon: str
    points: int = 0


class StorySegment(BaseModel):
    """Short story segment (2-3 sentences)"""
    id: str
    text: str  # 2-3 sentences, dyslexia-friendly
    visual_cues: List[VisualCue] = []
    multiple_choices: List[MultipleChoice]
    word_challenge: Optional[WordChallenge] = None
    vocabulary_words: List[str] = []
    difficulty_level: int = Field(ge=1, le=5)
    estimated_reading_time: int = Field(description="Seconds to read segment")


class PlayerProgress(BaseModel):
    """Track player's progress and performance"""
    current_segment_id: str
    segments_completed: List[str] = []
    correct_choices: int = 0
    incorrect_choices: int = 0
    hints_used: int = 0
    challenges_completed: int = 0
    current_difficulty: int = Field(ge=1, le=5, default=2)
    rewards_earned: List[Reward] = []
    session_start_time: datetime = Field(default_factory=datetime.now)
    total_reading_time: int = 0  # Seconds spent reading


class GameTurn(BaseModel):
    """Represents interaction with a story segment"""
    turn: int
    segment: StorySegment
    player_choice: Optional[str] = None  # Choice ID selected (legacy)
    user_input: Optional[str] = None  # The actual choice text displayed to user
    challenge_response: Optional[str] = None
    was_correct: bool = False
    hint_given: bool = False
    reward_earned: Optional[Reward] = None
    timestamp: float


class GameState(BaseModel):
    """Complete educational game state for dyslexia support"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    turn: int = 0
    genre: Literal['forest', 'space', 'dungeon', 'mystery']
    story_segments: List[StorySegment] = []
    current_segment_index: int = 0
    player_progress: PlayerProgress
    history: List[GameTurn] = []
    vocabulary_learned: List[str] = []
    game_over: bool = False
    backtrack_count: int = 0
    session_limit: int = Field(default=8, ge=5, le=10)  # 7-10 segments per session
    adaptive_difficulty: bool = True
    text_to_speech_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)


class GameStartRequest(BaseModel):
    """Request to start a new educational game"""
    genre: Literal['forest', 'space', 'dungeon', 'mystery']
    difficulty_level: int = Field(ge=1, le=5, default=2)
    session_limit: int = Field(ge=5, le=10, default=8)
    text_to_speech: bool = False


class GameStartResponse(BaseModel):
    """Response when starting a new educational game"""
    session_id: str
    first_segment: StorySegment
    player_progress: PlayerProgress
    session_info: Dict[str, Any]


class GameChoiceRequest(BaseModel):
    """Request when player makes a choice"""
    session_id: str
    segment_id: str
    choice_id: str
    turn: int


class GameChallengeRequest(BaseModel):
    """Request when player completes word challenge"""
    session_id: str
    segment_id: str
    challenge_response: str
    turn: int


class GameNextRequest(BaseModel):
    """Request for next turn (compatibility with traditional game frontend)"""
    session_id: str
    user_input: str
    turn: int


class GameNextResponse(BaseModel):
    """Response for next turn (compatibility with traditional game frontend)"""
    response: str
    turn: int
    vocabulary_words: List[str]
    game_over: bool
    choices: List[str] = []  # Dynamic choices for the current story segment


class TraditionalGameStartResponse(BaseModel):
    """Response for starting game (compatibility with traditional frontend)"""
    session_id: str
    story_intro: str
    turn: int


class GameInteractionResponse(BaseModel):
    """Response after player interaction"""
    is_correct: bool
    feedback: str
    hint: Optional[str] = None
    reward_earned: Optional[Reward] = None
    next_segment: Optional[StorySegment] = None
    player_progress: PlayerProgress
    game_over: bool = False
    session_complete: bool = False


class GameBacktrackRequest(BaseModel):
    """Request to backtrack to a previous turn"""
    session_id: str
    target_turn: int


class GameBacktrackResponse(BaseModel):
    """Response when backtracking"""
    restored_state: GameState
    message: str


class GameEndRequest(BaseModel):
    """Request to end the current game"""
    session_id: str


class GameEndResponse(BaseModel):
    """Response when ending game"""
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: Literal['healthy', 'degraded']
    gemini_available: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class VocabularyWord(BaseModel):
    """Vocabulary word definition"""
    word: str
    definition: str
    difficulty: Literal['easy', 'medium', 'hard']
    category: str
    example: Optional[str] = None
    synonyms: List[str] = []
    phonetic: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)
