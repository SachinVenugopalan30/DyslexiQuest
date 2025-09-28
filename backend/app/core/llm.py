# LLM integration for Gemini API

import asyncio
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import settings, GAME_CONFIG, GENRE_SETTINGS
from app.models.vocabulary import VOCABULARY_DATABASE, extract_vocabulary_from_text

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google's Gemini API for educational content generation"""
    
    def __init__(self):
        self.client = None
        self.model = None
        self.is_available = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            if not settings.gemini_api_key:
                logger.warning("No Gemini API key provided. Using fallback responses.")
                return
            
            genai.configure(api_key=settings.gemini_api_key)
            
            # Configure the model with safety settings for children
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                }
            )
            
            self.is_available = True
            logger.info("Gemini client initialized successfully for educational content")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.is_available = False
    
    async def check_health(self) -> bool:
        """Check if Gemini API is available"""
        if not self.is_available:
            return False
        
        try:
            # Simple test query
            response = await self.generate_response("Test", "fantasy", 1, [])
            return bool(response)
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
    
    async def generate_story_segment(self, segment_number: int, theme: Optional[str] = None, adventure_category: Optional[str] = None, adventure_info: Optional[dict] = None, previous_choices: Optional[list] = None, story_context: Optional[list] = None, story_state: Optional[dict] = None):
        """Generate a dynamic educational story segment with multiple-choice options"""
        
        # Always use the new dynamic story generation system
        if adventure_category and adventure_info:
            prompt = self._create_dynamic_adventure_prompt(segment_number, adventure_category, adventure_info, previous_choices, story_context, story_state)
        else:
            # Map old themes to new adventure categories
            theme_mapping = {
                'fantasy': 'dungeon',
                'adventure': 'forest', 
                'sci-fi': 'space',
                'mystery': 'mystery'
            }
            safe_theme = theme or 'forest'  # Ensure theme is not None
            mapped_theme = theme_mapping.get(safe_theme, 'forest')
            
            # Create basic adventure info for backward compatibility
            basic_adventure_info = {
                'name': f'{mapped_theme.title()} Adventure',
                'description': f'An exciting {mapped_theme} adventure',
                'themes': [],
                'vocabulary_focus': []
            }
            prompt = self._create_dynamic_adventure_prompt(segment_number, mapped_theme, basic_adventure_info, previous_choices, story_context, story_state)
        
        try:
            if not self.is_available or not self.model:
                fallback_data = self._get_fallback_segment(segment_number, adventure_category or theme or "forest")
                return self._convert_dict_to_story_segment(fallback_data)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse the structured response and convert to StorySegment
                segment_data = self._parse_segment_response(response.text.strip(), segment_number, adventure_category or theme or "forest")
                return self._convert_dict_to_story_segment(segment_data)
            else:
                fallback_data = self._get_fallback_segment(segment_number, adventure_category or theme or "forest")
                return self._convert_dict_to_story_segment(fallback_data)
                
        except Exception as e:
            logger.error(f"Error generating dynamic story segment: {e}")
            fallback_data = self._get_fallback_segment(segment_number, adventure_category or theme or "forest")
            return self._convert_dict_to_story_segment(fallback_data)
    
    async def generate_new_story_beginning(self, theme: str):
        """Generate a completely new story beginning for the specified theme"""
        
        from app.api.prompts import get_dynamic_story_creation_prompt, get_system_prompt, get_turn_progression_prompt
        
        try:
            if not self.is_available or not self.model:
                return self._get_fallback_segment(1, theme)
            
            # Create a comprehensive prompt for generating a brand new story
            system_prompt = get_system_prompt()
            theme_creation_prompt = get_dynamic_story_creation_prompt(theme)
            progression_prompt = get_turn_progression_prompt(1)
            
            full_prompt = f"""{system_prompt}

{theme_creation_prompt}

{progression_prompt}

TASK: Create the opening segment of a BRAND NEW {theme} adventure story.

CRITICAL REQUIREMENTS:
        - This is turn 1 of 10 - set up an engaging beginning
- Create 2-3 sentences that establish a unique scenario
- Include visual emojis to make it engaging  
- Present exactly 4 different choice options
- Each choice should lead to a different but valid story path
- All choices are correct - there are no wrong answers
- Keep language simple and dyslexia-friendly
- Include 1-2 vocabulary words naturally in context
- End with a clear question about what to do first

FORMAT YOUR RESPONSE EXACTLY AS:
STORY: [Your 2-3 sentence story opening with emojis]
CHOICE1: [Option A - 3-6 words with emoji]
CHOICE2: [Option B - 3-6 words with emoji]  
CHOICE3: [Option C - 3-6 words with emoji]
CHOICE4: [Option D - 3-6 words with emoji]
CHALLENGE_TYPE: completion
CHALLENGE_WORD: [simple vocabulary word related to the theme]
CHALLENGE_PROMPT: [Simple word completion challenge]

Generate a completely unique {theme} adventure beginning now:"""

            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                logger.info(f"LLM Response for new story beginning: {response.text.strip()}")
                segment_data = self._parse_segment_response(response.text.strip(), 1, theme)
                logger.info(f"Parsed segment data: {segment_data}")
                return self._convert_dict_to_story_segment(segment_data)
            else:
                logger.warning("No response from LLM, using fallback")
                fallback_data = self._get_fallback_segment(1, theme)
                return self._convert_dict_to_story_segment(fallback_data)
                
        except Exception as e:
            logger.error(f"Error generating new story beginning: {e}")
            fallback_data = self._get_fallback_segment(1, theme)
            return self._convert_dict_to_story_segment(fallback_data)
    
    def _convert_dict_to_story_segment(self, segment_data: Dict[str, Any]):
        """Convert dictionary data to StorySegment object"""
        from app.models.game import StorySegment, MultipleChoice, WordChallenge, VisualCue
        import uuid
        
        # Create multiple choice objects
        choices = []
        for choice_data in segment_data.get("choices", []):
            visual_cue = None
            if choice_data.get("text"):
                # Extract emoji from choice text if present
                visual_cue = VisualCue(
                    icon="✨",
                    description="Choice indicator",
                    position="before"
                )
            
            choice = MultipleChoice(
                id=choice_data.get("id", "A"),
                text=choice_data.get("text", "Continue"),
                is_correct=choice_data.get("is_correct", True),
                feedback=choice_data.get("feedback", ""),
                visual_cue=visual_cue
            )
            choices.append(choice)
        
        # Create word challenge if available
        word_challenge = None
        if segment_data.get("challenge"):
            challenge_data = segment_data["challenge"]
            # Map challenge types to valid model values
            raw_type = challenge_data.get("type", "completion")
            
            # Ensure we use valid literal types
            if raw_type in ['word_completion', 'completion']:
                challenge_type = 'completion'
            elif raw_type in ['word_matching', 'matching']:
                challenge_type = 'matching'
            elif raw_type == 'spelling':
                challenge_type = 'spelling'
            elif raw_type == 'rhyme':
                challenge_type = 'rhyme'
            else:
                challenge_type = 'completion'  # Default fallback
                
            target_word = challenge_data.get("target_word", "adventure")
            
            word_challenge = WordChallenge(
                type=challenge_type,
                instruction=challenge_data.get("prompt", "Complete this word"),
                word=target_word,
                correct_answer=target_word,
                hint="Sound it out carefully!",
                difficulty_level=1
            )
        
        # Create story segment
        story_segment = StorySegment(
            id=str(uuid.uuid4()),
            text=segment_data.get("story", "Your adventure begins!"),
            question=segment_data.get("question", "What do you want to do next?"),
            multiple_choices=choices,
            word_challenge=word_challenge,
            visual_cues=[],
            vocabulary_words=[],
            difficulty_level=1,
            estimated_reading_time=30
        )
        
        return story_segment
    
    async def generate_educational_round(self, round_number: int, theme: str, difficulty: str) -> Dict[str, Any]:
        """Generate an educational round with progressive difficulty for children aged 5-10"""
        
        from app.api.prompts import get_educational_round_prompt
        
        prompt = get_educational_round_prompt(round_number, theme, difficulty)
        
        try:
            if not self.is_available or not self.model:
                return self._get_fallback_educational_round(round_number, theme, difficulty)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse the structured response
                round_data = self._parse_educational_round_response(response.text.strip(), round_number, theme, difficulty)
                return round_data
            else:
                return self._get_fallback_educational_round(round_number, theme, difficulty)
                
        except Exception as e:
            logger.error(f"Error generating educational round: {e}")
            return self._get_fallback_educational_round(round_number, theme, difficulty)

    async def generate_hint_for_wrong_answer(self, question: str, correct_answer: str, wrong_answer: str, theme: str) -> str:
        """Generate a helpful hint when child picks wrong answer"""
        
        from app.api.prompts import get_hint_generation_prompt
        
        prompt = get_hint_generation_prompt(question, correct_answer, wrong_answer, theme)
        
        try:
            if not self.is_available or not self.model:
                return self._get_fallback_hint_for_child(correct_answer)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()[:100]  # Keep hints very short for children
            else:
                return self._get_fallback_hint_for_child(correct_answer)
                
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return self._get_fallback_hint_for_child(correct_answer)

    async def generate_story_completion(self, theme: str, story_context: str, player_choices: list) -> str:
        """Generate a satisfying story conclusion"""
        
        from app.api.prompts import get_story_completion_prompt
        
        prompt = get_story_completion_prompt(theme, story_context, player_choices)
        
        try:
            if not self.is_available or not self.model:
                return self._get_fallback_completion(theme)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_completion(theme)
                
        except Exception as e:
            logger.error(f"Error generating story completion: {e}")
            return self._get_fallback_completion(theme)

    async def generate_adaptive_hint(self, challenge_type: str, difficulty: str, context: str) -> str:
        """Generate adaptive hints for word challenges based on player performance"""
        prompt = self._create_hint_prompt(challenge_type, difficulty, context)
        
        try:
            if not self.is_available or not self.model:
                return self._get_fallback_hint(challenge_type)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()[:200]  # Keep hints concise
            else:
                return self._get_fallback_hint(challenge_type)
                
        except Exception as e:
            logger.error(f"Error generating adaptive hint: {e}")
            return self._get_fallback_hint(challenge_type)
    
    async def generate_response(
        self, 
        user_input: str, 
        genre: str, 
        turn: int, 
        history: list
    ) -> tuple[str, list[str]]:
        """Generate AI response to user input"""
        
        prompt = self._create_response_prompt(user_input, genre, turn, history)
        
        try:
            if not self.is_available or not self.model:
                return self._get_fallback_response(user_input, genre, turn)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                result = response.text.strip()
                
                # Extract vocabulary words
                vocab_words = extract_vocabulary_from_text(result)
                
                # Ensure appropriate length
                if len(result) > GAME_CONFIG["RESPONSE_MAX_LENGTH"]:
                    result = result[:GAME_CONFIG["RESPONSE_MAX_LENGTH"]] + "..."
                
                # Check if game should end
                if turn >= GAME_CONFIG["MAX_TURNS"] - 1:
                    result += "\n\nGAME OVER – Thanks for playing!"
                
                return result, vocab_words
            else:
                return self._get_fallback_response(user_input, genre, turn)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response(user_input, genre, turn)
    
    def _create_intro_prompt(self, genre: str) -> str:
        """Create the system prompt for story introduction"""
        genre_info = GENRE_SETTINGS.get(genre, GENRE_SETTINGS["adventure"])
        vocab_sample = list(VOCABULARY_DATABASE.keys())[:10]
        return f"""You are a friendly storyteller for children aged 8-14, creating a {genre_info['name']} in DyslexiQuest's accessible adventure style.

IMPORTANT RULES:
- Keep responses under 80 words
- Use simple, age-appropriate language suitable for children with dyslexia
- Include 1-2 vocabulary words from this list when natural: {', '.join(vocab_sample)}
- Make the story exciting but never scary or violent
- Use short paragraphs (2-4 lines maximum)
- Create puzzle-based challenges that require thinking
- Be encouraging and positive
- End each response with a question or choice for the player

GENRE: {genre_info['name']}
THEMES: {', '.join(genre_info['themes'])}

Create an engaging story introduction that starts the adventure. Include a clear situation and ask what the player wants to do first."""

    def _create_dynamic_adventure_prompt(self, segment_number: int, adventure_category: str, adventure_info: dict, previous_choices: Optional[list] = None, story_context: Optional[list] = None, story_state: Optional[dict] = None) -> str:
        """Create prompt for dynamic adventure-based story generation"""
        
        from app.api.prompts import get_system_prompt, get_turn_progression_prompt
        
        context = ""
        current_choice = ""
        if previous_choices:
            context = f"Previous choices made: {', '.join(previous_choices[-3:])}"
            # Get the most recent choice the player just made
            if len(previous_choices) > 0:
                current_choice = f"PLAYER'S MOST RECENT CHOICE: \"{previous_choices[-1]}\""
        
        # Add story context for better continuity
        story_history = ""
        if story_context and len(story_context) > 0:
            story_history = f"\nPrevious story segments:\n{chr(10).join(story_context[-2:])}"
        
        # Get turn-specific progression guidance
        progression_prompt = get_turn_progression_prompt(segment_number)
        
        # Theme-specific elements
        theme_elements = {
            'forest': {
                'emojis': '🌲🦉🌿🦌✨🍄🌸🦋🐿️🌳',
                'vocab_words': 'forest, trees, animals, nature, explore, discover, adventure, wisdom, harmony, magical'
            },
            'space': {
                'emojis': '🚀🪐👽⭐🌌🛸💫🌟🔭🌠',
                'vocab_words': 'space, planet, rocket, stars, explore, galaxy, cosmic, adventure, discovery, technology'
            },
            'dungeon': {
                'emojis': '🏰✨💎🔮🗝️🚪💰🧙‍♂️🎭🏛️',
                'vocab_words': 'magic, treasure, crystal, puzzle, explore, discover, mystery, ancient, enchanted, wisdom'
            },
            'mystery': {
                'emojis': '🔍🕵️📚❓🔐💡📜🏛️🎯🧩',
                'vocab_words': 'mystery, clues, detective, solve, help, discover, investigate, evidence, puzzle, solution'
            }
        }
        
        theme_info = theme_elements.get(adventure_category, theme_elements['forest'])
        
        return f"""{get_system_prompt()}

{progression_prompt}

ADVENTURE TYPE: {adventure_info['name']}
SEGMENT NUMBER: {segment_number} of 10 total segments
{context}{story_history}

{current_choice}

DYNAMIC STORY GENERATION REQUIREMENTS:
- CREATE A UNIQUE CONTINUATION - never repeat previous segments
- Build directly on the player's previous choices and story context
- CRITICAL: Respond specifically to the player's most recent choice - make it meaningful!
- 2-3 short sentences maximum (dyslexia-friendly)
- Focus on {adventure_category} adventure themes
- Include visual emojis: {theme_info['emojis']}
- Use vocabulary words naturally: {theme_info['vocab_words']}
- Create EXACTLY 4 multiple-choice options (never less!)
- Each choice should be 3-6 words maximum for easy reading
- Include one word challenge appropriate for the story
- Neutral tone - never scary or violent, but avoid overly encouraging language
- Clear visual descriptions with emojis
- ADVANCE THE PLOT - make meaningful progress in the story
- All 4 choices should lead to different but equally valid story paths
- Ensure the story can conclude satisfactorily within 10 turns
- NEVER include encouraging phrases like "Great choice!" or "Excellent!" - keep responses neutral and factual

FORMAT YOUR RESPONSE EXACTLY AS:
STORY: [2-3 sentences that continue the adventure with emojis]
QUESTION: [A clear, simple question about what happened in the story - max 8 words]
CHOICE1: [Option A - 3-6 words with emoji]
CHOICE2: [Option B - 3-6 words with emoji]  
CHOICE3: [Option C - 3-6 words with emoji]
CHOICE4: [Option D - 3-6 words with emoji]
CHALLENGE_TYPE: completion
CHALLENGE_WORD: [vocabulary word related to the theme]
CHALLENGE_PROMPT: [Simple word completion challenge]

IMPORTANT: The QUESTION should be directly related to the STORY content and have ONE clear correct answer among the choices.

Generate the next unique segment of this {adventure_category} adventure:"""
    
    def _create_adventure_prompt(self, segment_number: int, adventure_category: str, adventure_info: dict, previous_choices: Optional[list] = None, story_context: Optional[list] = None) -> str:
        """Create prompt for new adventure-based story generation (legacy method)"""
        
        # Use the new dynamic method
        return self._create_dynamic_adventure_prompt(segment_number, adventure_category, adventure_info, previous_choices, story_context, None)

    def _create_segment_prompt(self, segment_number: int, theme: str, previous_choices: Optional[list] = None, story_context: Optional[list] = None) -> str:
        """Create prompt for educational story segment generation"""
        
        vocab_sample = list(VOCABULARY_DATABASE.keys())[:10]
        context = ""
        if previous_choices:
            context = f"Previous choices made: {', '.join(previous_choices[-3:])}"
        
        # Add story context for better continuity
        story_history = ""
        if story_context and len(story_context) > 0:
            story_history = f"\nPrevious story segments:\n{chr(10).join(story_context[-2:])}"
        
        # Story progression guidance
        progression_guidance = ""
        if segment_number == 1:
            progression_guidance = "This is the beginning of the story. Set up the adventure and introduce the main character/situation."
        elif segment_number <= 3:
            progression_guidance = "Continue developing the story from previous choices. Build on what happened before and introduce new challenges or discoveries."
        elif segment_number <= 6:
            progression_guidance = "The story is progressing well. Add complications, mysteries, or exciting discoveries that build toward a resolution."
        else:
            progression_guidance = "The story is nearing its conclusion. Start building toward a satisfying resolution of the adventure."
        
        return f"""Create an educational story segment for children aged 5-12 with dyslexia.

SEGMENT NUMBER: {segment_number} of 7-10 total segments
THEME: {theme}
{context}{story_history}

STORY PROGRESSION: {progression_guidance}

CRITICAL REQUIREMENTS:
- CONTINUE THE STORY - don't restart or repeat previous content
- Build directly on the player's previous choices
- 2-3 short sentences maximum (dyslexia-friendly) 
- Include visual cues like ✨🌟🎯🦋🏰 where appropriate
- Age-appropriate vocabulary with 1-2 words from: {', '.join(vocab_sample)}
- Create EXACTLY 4 multiple-choice options (never less!)
- Each choice should be 3-6 words maximum for easy reading
- Include one embedded word challenge (completion, matching, or spelling)
- Positive, encouraging tone - never scary
- Clear visual descriptions with emojis
- MAKE EACH SEGMENT DIFFERENT - advance the plot!

FORMAT YOUR RESPONSE AS:
STORY: [2-3 sentences that continue from previous choices with visual cues and emojis]
CHOICE1: [Option A - 3-6 words with emoji]
CHOICE2: [Option B - 3-6 words with emoji]  
CHOICE3: [Option C - 3-6 words with emoji]
CHOICE4: [Option D - 3-6 words with emoji]
CHALLENGE_TYPE: [completion|matching|spelling|rhyme]
CHALLENGE_WORD: [target vocabulary word]
CHALLENGE_PROMPT: [What should the player do?]

EXAMPLE:
STORY: You enter a ✨magical garden✨ where flowers sing beautiful songs! A friendly butterfly 🦋 lands on your shoulder and whispers about hidden treasure.
CHOICE1: Follow the butterfly 🦋
CHOICE2: Listen to singing flowers 🌺
CHOICE3: Explore the sparkling pond ✨
CHOICE4: Look for the treasure 💰
CHALLENGE_TYPE: completion
CHALLENGE_WORD: garden
CHALLENGE_PROMPT: Complete this word: g_rd_n (a place where flowers grow)"""
    
    def _create_response_prompt(self, user_input: str, genre: str, turn: int, history: list) -> str:
        """Create the prompt for continuing the story (legacy method for backward compatibility)"""
        
        genre_info = GENRE_SETTINGS.get(genre, GENRE_SETTINGS["adventure"])
        vocab_sample = list(VOCABULARY_DATABASE.keys())[:15]
        
        # Build context from recent history
        context = ""
        if history:
            recent_history = history[-3:]  # Last 3 turns for context
            context = "\n".join([
                f"Turn {h['turn']}: Player chose: {h['user_input']}\nYou responded: {h['ai_response']}"
                for h in recent_history
            ])
        
        return f"""You are continuing a {genre_info['name']} for children aged 5-12 with dyslexia. This is turn {turn} of maximum 10 turns.

CONTEXT FROM RECENT STORY:
{context}

PLAYER'S CURRENT CHOICE: {user_input}

CRITICAL REQUIREMENTS:
- Write 2-3 short sentences (dyslexia-friendly)
- ADAPT the story based on the player's choice - make it meaningful!
- Use simple words and include 1 vocabulary word from: {', '.join(vocab_sample[:8])}
- Add visual emoji cues (✨🌟🏰🌳🦋🔑)
- Never be scary or violent - keep it magical and safe
- All 4 choices should lead to different but equally interesting story paths
- Each choice should be 3-6 words maximum
- Make choices clear and different from each other
- Keep language neutral - avoid encouraging phrases
- NEVER include encouraging phrases like "Great choice!" or "Excellent!" - keep responses neutral and factual
        - If this is turn {turn} of 10, start building toward a satisfying conclusion
        - If this is turn 8-10, wrap up the story with a happy endingFORMAT EXAMPLE:
[Your 2-3 sentence story response that directly responds to their choice with emojis]

What happens next in your adventure?
1. [Choice that builds on the player's decision] 🦋
2. [Different path that respects their choice] 💰  
3. [Another interesting direction] 🧙‍♂️
4. [Creative alternative based on their action] 🌺

ADAPT YOUR STORY TO THE PLAYER'S CHOICE: {user_input}"""
    
    def _create_hint_prompt(self, challenge_type: str, difficulty: str, context: str) -> str:
        """Create prompt for adaptive hints"""
        
        return f"""Create a helpful hint for a child with dyslexia working on a {challenge_type} challenge.

CONTEXT: {context}
DIFFICULTY: {difficulty}

REQUIREMENTS:
- Maximum 20 words
- Use simple, encouraging language
- Include visual or phonetic cues
- Be patient and positive
- Help without giving the full answer
- Use emojis to make it friendlier

EXAMPLES:
For completion: "Try sounding it out! 🔤 Think about the letters that make the 'ar' sound."
For spelling: "Remember, this word rhymes with 'start'! 🎵 What letters make that sound?"
For matching: "Look for the word that means the same thing! 🔍 Think about what makes you happy."

Generate a similar hint for this challenge."""

    def _parse_segment_response(self, response_text: str, segment_number: int, theme: str) -> Dict[str, Any]:
        """Parse the LLM response into structured segment data"""
        
        lines = response_text.split('\n')
        segment_data = {
            "segment_number": segment_number,
            "theme": theme,
            "story": "",
            "question": "",
            "choices": [],
            "challenge": None
        }
        
        challenge_data = {}
        story_lines = []  # Collect story lines before first CHOICE
        found_choices = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("STORY:"):
                segment_data["story"] = line.replace("STORY:", "").strip()
                found_choices = True  # Mark that we're now in structured mode
            elif line.startswith("QUESTION:"):
                segment_data["question"] = line.replace("QUESTION:", "").strip()
            elif line.startswith("CHOICE1:"):
                segment_data["choices"].append({"id": "A", "text": line.replace("CHOICE1:", "").strip(), "is_correct": True})
                found_choices = True
            elif line.startswith("CHOICE2:"):
                segment_data["choices"].append({"id": "B", "text": line.replace("CHOICE2:", "").strip(), "is_correct": True})
            elif line.startswith("CHOICE3:"):
                segment_data["choices"].append({"id": "C", "text": line.replace("CHOICE3:", "").strip(), "is_correct": True})
            elif line.startswith("CHOICE4:"):
                segment_data["choices"].append({"id": "D", "text": line.replace("CHOICE4:", "").strip(), "is_correct": True})
            elif line.startswith("CHALLENGE_TYPE:"):
                challenge_data["type"] = line.replace("CHALLENGE_TYPE:", "").strip()
            elif line.startswith("CHALLENGE_WORD:"):
                challenge_data["word"] = line.replace("CHALLENGE_WORD:", "").strip()
            elif line.startswith("CHALLENGE_PROMPT:"):
                challenge_data["prompt"] = line.replace("CHALLENGE_PROMPT:", "").strip()
            elif not found_choices:
                # If we haven't found any structured elements yet, treat this as story text
                story_lines.append(line)
        
        # If no explicit STORY: was found, use the collected story lines
        if not segment_data["story"] and story_lines:
            segment_data["story"] = " ".join(story_lines)
        
        # Create challenge object if we have the required data
        if all(key in challenge_data for key in ["type", "word", "prompt"]):
            segment_data["challenge"] = {
                "type": challenge_data["type"],
                "target_word": challenge_data["word"],
                "prompt": challenge_data["prompt"],
                "difficulty": "easy"  # Default difficulty
            }
        
        # Ensure we have exactly 4 choices - if not, let it fail so template system is used
        if len(segment_data["choices"]) < 4:
            raise ValueError(f"LLM response only contained {len(segment_data['choices'])} choices, expected 4")
        
        return segment_data

    def _get_fallback_intro(self, genre: str) -> str:
        """Get fallback introduction when API is unavailable"""
        fallback_intros = {
            "fantasy": "Welcome, brave adventurer! You stand before an ancient castle with glowing windows. A friendly wizard waves from a tower window. The enchanted forest whispers secrets in the wind. What do you want to explore first?",
            
            "adventure": "Ahoy, treasure hunter! You've discovered an old map leading to a mysterious island. Your ship has just reached the sandy shore. Palm trees sway gently, and you can see a cave in the distance. Where do you want to start your expedition?",
            
            "mystery": "Hello, detective! You've arrived at a curious mansion where something mysterious has happened. The friendly butler greets you with a warm smile. There are interesting clues waiting to be found. Which room would you like to investigate first?",
            
            "sci-fi": "Greetings, space explorer! Your spaceship has landed on a beautiful alien planet with purple skies and silver trees. Strange but friendly creatures watch you curiously from behind crystal rocks. Your scanner detects something interesting nearby. What do you want to discover first?"
        }
        
        return fallback_intros.get(genre, fallback_intros["adventure"])
    
    def _get_fallback_response(self, user_input: str, genre: str, turn: int) -> tuple[str, list[str]]:
        """Get fallback response when API is unavailable"""
        
        # Simple pattern matching for common actions
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["look", "examine", "see"]):
            responses = [
                "You discover something magnificent! The ancient walls tell stories of brave adventurers. A mysterious symbol catches your eye. What would you like to examine more closely?",
                "Your keen eyes spot something interesting! There's a beautiful crystal that seems to illuminate the area. The treasure might be nearby. What's your next move?",
                "You observe your surroundings with wisdom! A hidden portal becomes visible when you look carefully. This expedition is full of surprises! Where do you want to explore?"
            ]
        elif any(word in user_lower for word in ["go", "move", "walk", "north", "south", "east", "west"]):
            responses = [
                "You courageously move forward! The path leads to an enchanted garden with singing flowers. A friendly guardian appears to help you. What do you want to ask them?",
                "You discover a sanctuary filled with glowing books. Each chronicle contains different stories. Which one interests you most?",
                "You transform your journey by choosing a new direction! Ahead lies a magnificent labyrinth made of silver and gold. Do you want to solve its riddle?"
            ]
        elif any(word in user_lower for word in ["talk", "speak", "ask", "say"]):
            responses = [
                "The character smiles warmly and shares their wisdom! They tell you about a hidden treasure that requires perseverance to find. They offer to help with your quest. Do you accept their guidance?",
                "Your friendly conversation reveals important clues! They mention an ancient expedition that discovered something wonderful nearby. Would you like to hear the complete chronicle?",
                "They greet you with enthusiasm! This guardian knows many secrets about the mysterious portal ahead. They're willing to illuminate the path for brave adventurers like you. What do you want to learn?"
            ]
        else:
            responses = [
                "Your action leads to an unexpected discovery. The mysterious puzzle begins to make sense. What's your next move?",
                "Something happens as a result of your actions. The ancient magic responds. How do you want to continue?",
                "Your actions transform the situation. The enchanted surroundings change. What would you like to discover next?"
            ]
        
        import random
        response = random.choice(responses)
        
        # Add ending if near max turns
        if turn >= GAME_CONFIG["MAX_TURNS"] - 1:
            response += " Adventure complete."
        
        # Extract vocabulary words from the response
        vocab_words = extract_vocabulary_from_text(response)
        
        return response, vocab_words
    
    def _get_fallback_segment(self, segment_number: int, theme: str) -> Dict[str, Any]:
        """Get fallback educational story segment when API is unavailable"""
        
        # This function is deprecated and will be removed.
        # For now, it returns a minimal structure to avoid breaking changes.
        return {
            "segment_number": segment_number,
            "theme": theme,
            "story": "The adventure continues...",
            "choices": [],
            "challenge": None
        }
    
    def _get_fallback_hint(self, challenge_type: str) -> str:
        """Get fallback hint when API is unavailable"""
        
        hints = {
            "completion": "Try sounding out the missing letters! 🔤 Think about what sounds you hear in the word.",
            "matching": "Think about what the word means! 🤔 Which choice has the same meaning?",
            "spelling": "Say the word slowly and listen to each sound! 🎵 What letters make those sounds?",
            "rhyme": "Think of words that sound similar! 🎵 What word rhymes with this one?"
        }
        
        return hints.get(challenge_type, "You're doing great! 🌟 Take your time and try your best!")
    
    def _parse_educational_round_response(self, response_text: str, round_number: int, theme: str, difficulty: str) -> Dict[str, Any]:
        """Parse the LLM response for educational rounds"""
        
        lines = response_text.split('\n')
        round_data = {
            "round_number": round_number,
            "theme": theme,
            "difficulty": difficulty,
            "story": "",
            "question": "",
            "choices": [],
            "correct": 0,
            "hint": "",
            "word": ""
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("STORY:"):
                round_data["story"] = line.replace("STORY:", "").strip()
            elif line.startswith("QUESTION:"):
                round_data["question"] = line.replace("QUESTION:", "").strip()
            elif line.startswith("CHOICE_A:"):
                round_data["choices"].append(line.replace("CHOICE_A:", "").strip())
            elif line.startswith("CHOICE_B:"):
                round_data["choices"].append(line.replace("CHOICE_B:", "").strip())
            elif line.startswith("CHOICE_C:"):
                round_data["choices"].append(line.replace("CHOICE_C:", "").strip())
            elif line.startswith("CORRECT:"):
                correct_letter = line.replace("CORRECT:", "").strip().upper()
                if correct_letter == 'A':
                    round_data["correct"] = 0
                elif correct_letter == 'B':
                    round_data["correct"] = 1
                elif correct_letter == 'C':
                    round_data["correct"] = 2
                else:
                    # Default to first choice if parsing fails
                    logger.warning(f"Could not parse correct answer '{correct_letter}', defaulting to A")
                    round_data["correct"] = 0
            elif line.startswith("HINT:"):
                round_data["hint"] = line.replace("HINT:", "").strip()
            elif line.startswith("CHALLENGE_WORD:"):
                round_data["word"] = line.replace("CHALLENGE_WORD:", "").strip()
        
        # Ensure we have all required data
        if not round_data["choices"]:
            round_data["choices"] = ["Option A", "Option B", "Option C"]
        
        if len(round_data["choices"]) < 3:
            while len(round_data["choices"]) < 3:
                round_data["choices"].append("Try again")
        
        # Validate correct index
        if round_data["correct"] >= len(round_data["choices"]):
            logger.warning(f"Correct index {round_data['correct']} is out of range for {len(round_data['choices'])} choices, setting to 0")
            round_data["correct"] = 0
        
        # Log the parsed data for debugging
        logger.info(f"Parsed educational round: question='{round_data['question']}', choices={round_data['choices']}, correct={round_data['correct']}")
        
        return round_data
    
    def _get_fallback_educational_round(self, round_number: int, theme: str, difficulty: str) -> Dict[str, Any]:
        """Get fallback educational round when API is unavailable"""
        
        # Simple fallback rounds based on difficulty and theme
        if difficulty == "easy":
            if theme == "forest":
                return {
                    "round_number": round_number,
                    "theme": theme,
                    "difficulty": difficulty,
                    "story": "A wise owl 🦉 sits on a tall tree branch. The owl watches over the peaceful forest below.",
                    "question": "Where does the owl sit?",
                    "choices": ["tree branch 🌳", "flower bed 🌸", "rock pile 🪨"],
                    "correct": 0,
                    "hint": "Look at the story! 🌳 Where do owls perch high up in the forest?",
                    "word": "branch"
                }
            else:  # space theme
                return {
                    "round_number": round_number,
                    "theme": theme,
                    "difficulty": difficulty,
                    "story": "A shiny rocket 🚀 travels through space to explore distant planets and meet alien friends.",
                    "question": "What does the rocket explore in space?",
                    "choices": ["planets 🪐", "houses �", "books 📚"],
                    "correct": 0,
                    "hint": "Think about space! 🪐 What round objects does the rocket visit far from Earth?",
                    "word": "planets"
                }
        elif difficulty == "intermediate":
            return {
                "round_number": round_number,
                "theme": theme,
                "difficulty": difficulty,
                "story": "Complete this word: The cat wants to go h_me 🏠",
                "question": "Complete the word: h_me",
                "choices": ["home 🏠", "hope 🌟", "hole 🕳️"],
                "correct": 0,
                "hint": "Where do you live? 🏠 A safe, warm place!",
                "word": "home"
            }
        else:  # difficult
            return {
                "round_number": round_number,
                "theme": theme,
                "difficulty": difficulty,
                "story": "The animals work together to help each other. They are kind and caring friends.",
                "question": "What does 'together' mean?",
                "choices": ["with friends 👫", "all alone 😔", "far away 🏃"],
                "correct": 0,
                "hint": "Think about friendship! 👫 When people help each other.",
                "word": "together"
            }
    
    def _get_fallback_hint_for_child(self, correct_answer: str) -> str:
        """Get fallback hint for children when API is unavailable"""
        
        encouraging_hints = [
            f"Try again! 🌟 Think about the word '{correct_answer}'.",
            f"Good try! 🤔 Sound out '{correct_answer}' slowly.",
            f"You're learning! 😊 The answer is about '{correct_answer}'.",
            f"Keep trying! 💪 What do you know about '{correct_answer}'?"
        ]
        
        import random
        return random.choice(encouraging_hints)

    def _get_fallback_completion(self, theme: str) -> str:
        """Get fallback completion when API is unavailable"""
        
        completions = {
            "forest": "🌲✨ Your forest adventure comes to a wonderful end! The wise animals thank you for your kindness, and the magical trees share their ancient wisdom with you. You return home with new friends and amazing memories! 🦋🌟",
            "space": "🚀🌌 What an incredible space adventure! You've explored distant planets and made friends with peaceful aliens. Your cosmic journey ends as you pilot your ship back to Earth, filled with wonder about the universe! ⭐💫",
            "dungeon": "🏰💎 Your dungeon quest reaches a magical conclusion! The ancient puzzles are solved, and you've discovered the greatest treasure of all - knowledge and courage. The castle celebrates your wisdom! ✨🎉",
            "mystery": "🔍💡 Mystery solved! Your detective skills have uncovered all the secrets and helped everyone involved. The grateful community celebrates your clever thinking and kind heart! 🎯🌟"
        }
        
        return completions.get(theme, completions["forest"])


# Global Gemini client instance
gemini_client = GeminiClient()


# Global Gemini client instance
gemini_client = GeminiClient()
