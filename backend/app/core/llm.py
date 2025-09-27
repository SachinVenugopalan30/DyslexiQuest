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
    
    async def generate_story_segment(self, segment_number: int, theme: Optional[str] = None, adventure_category: Optional[str] = None, adventure_info: Optional[dict] = None, previous_choices: Optional[list] = None, story_context: Optional[list] = None) -> Dict[str, Any]:
        """Generate an educational story segment with multiple-choice options"""
        # Use new adventure system if provided, fall back to old theme system
        if adventure_category and adventure_info:
            prompt = self._create_adventure_prompt(segment_number, adventure_category, adventure_info, previous_choices, story_context)
        else:
            prompt = self._create_segment_prompt(segment_number, theme or "adventure", previous_choices, story_context)
        
        try:
            if not self.is_available:
                return self._get_fallback_segment(segment_number, theme)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse the structured response
                return self._parse_segment_response(response.text.strip(), segment_number, theme or "adventure")
            else:
                return self._get_fallback_segment(segment_number, theme or "adventure")
                
        except Exception as e:
            logger.error(f"Error generating story segment: {e}")
            return self._get_fallback_segment(segment_number, theme or "adventure")
    
    async def generate_adaptive_hint(self, challenge_type: str, difficulty: str, context: str) -> str:
        """Generate adaptive hints for word challenges based on player performance"""
        prompt = self._create_hint_prompt(challenge_type, difficulty, context)
        
        try:
            if not self.is_available:
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
            if not self.is_available:
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

    def _create_adventure_prompt(self, segment_number: int, adventure_category: str, adventure_info: dict, previous_choices: Optional[list] = None, story_context: Optional[list] = None) -> str:
        """Create prompt for new adventure-based story generation"""
        
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
            progression_guidance = f"This is the beginning of the {adventure_info['name']}. Set up the adventure and introduce the main character/situation in this {adventure_info['description']}."
        elif segment_number <= 3:
            progression_guidance = f"Continue developing the {adventure_info['name']} from previous choices. Build on what happened before and introduce new challenges or discoveries."
        elif segment_number <= 6:
            progression_guidance = f"The {adventure_info['name']} is progressing well. Add complications, mysteries, or exciting discoveries that build toward a resolution."
        else:
            progression_guidance = f"The {adventure_info['name']} is nearing its conclusion. Start building toward a satisfying resolution of the adventure."
        
        themes_str = ', '.join(adventure_info['themes'])
        vocab_focus_str = ', '.join(adventure_info['vocabulary_focus'])
        
        return f"""Create an educational story segment for children aged 5-12 with dyslexia.

ADVENTURE TYPE: {adventure_info['name']}
ADVENTURE DESCRIPTION: {adventure_info['description']}
SEGMENT NUMBER: {segment_number} of 7-10 total segments
ADVENTURE THEMES: {themes_str}
{context}{story_history}

STORY PROGRESSION: {progression_guidance}

CRITICAL REQUIREMENTS:
- CONTINUE THE STORY - don't restart or repeat previous content
- Build directly on the player's previous choices
- 2-3 short sentences maximum (dyslexia-friendly)
- Focus on these adventure elements: {themes_str}
- Include visual cues like ✨🌟🎯🦋🏰🌲🚀👽🔍 where appropriate
- Use vocabulary focused on: {vocab_focus_str}
- Create EXACTLY 4 multiple-choice options (never less!)
- Each choice should be 3-6 words maximum for easy reading
- Include one embedded word challenge (completion, matching, or spelling)
- Positive, encouraging tone - never scary or violent
- Clear visual descriptions with emojis
- MAKE EACH SEGMENT DIFFERENT - advance the plot!
- All 4 choices should lead to different but equally valid story paths

FORMAT YOUR RESPONSE AS:
STORY: [2-3 sentences that continue from previous choices with visual cues and emojis focused on {adventure_category} adventure]
CHOICE1: [Option A - 3-6 words with emoji]
CHOICE2: [Option B - 3-6 words with emoji]  
CHOICE3: [Option C - 3-6 words with emoji]
CHOICE4: [Option D - 3-6 words with emoji]
CHALLENGE_TYPE: [word_completion|word_matching|spelling]
CHALLENGE_WORD: [target vocabulary word from {vocab_focus_str}]
CHALLENGE_PROMPT: [What should the player do?]

EXAMPLE FOR FOREST ADVENTURE:
STORY: You step into a magical forest 🌲 where friendly animals gather around a sparkling stream! A wise owl 🦉 perches on a branch and offers to be your guide.
CHOICE1: Follow the owl deeper 🦉
CHOICE2: Talk to forest animals 🦌
CHOICE3: Explore the sparkling stream ✨
CHOICE4: Climb the tallest tree 🌳
CHALLENGE_TYPE: word_completion
CHALLENGE_WORD: forest
CHALLENGE_PROMPT: Complete this word: f_r_st (where many trees grow together)"""

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
CHALLENGE_TYPE: [word_completion|word_matching|spelling]
CHALLENGE_WORD: [target vocabulary word]
CHALLENGE_PROMPT: [What should the player do?]

EXAMPLE:
STORY: You enter a ✨magical garden✨ where flowers sing beautiful songs! A friendly butterfly 🦋 lands on your shoulder and whispers about hidden treasure.
CHOICE1: Follow the butterfly 🦋
CHOICE2: Listen to singing flowers 🌺
CHOICE3: Explore the sparkling pond ✨
CHOICE4: Look for the treasure 💰
CHALLENGE_TYPE: word_completion
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
        
        return f"""You are continuing a {genre_info['name']} for children aged 5-12 with dyslexia. This is turn {turn} of maximum 15 turns.

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
- Include encouraging language
- If this is turn {turn} of 15, start building toward a satisfying conclusion
- If this is turn 13-15, wrap up the story with a happy ending

FORMAT EXAMPLE:
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
For word_completion: "Try sounding it out! 🔤 Think about the letters that make the 'ar' sound."
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
            "choices": [],
            "challenge": None
        }
        
        challenge_data = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("STORY:"):
                segment_data["story"] = line.replace("STORY:", "").strip()
            elif line.startswith("CHOICE1:"):
                segment_data["choices"].append({"id": "A", "text": line.replace("CHOICE1:", "").strip(), "is_correct": True})
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
                "Your adventure continues! You discover a sanctuary filled with glowing books. Each chronicle contains different stories. Which one interests you most?",
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
                "What an excellent idea! Your creative thinking leads to an unexpected discovery. The mysterious puzzle begins to make sense. You're making great progress on this adventure! What's your next brilliant move?",
                "Your courage and wisdom guide you well! Something magnificent happens as a result of your actions. The ancient magic responds to your perseverance. How do you want to continue your expedition?",
                "Brilliant choice, young explorer! Your actions transform the situation in a wonderful way. The enchanted surroundings seem to approve of your decision. What would you like to discover next?"
            ]
        
        import random
        response = random.choice(responses)
        
        # Add ending if near max turns
        if turn >= GAME_CONFIG["MAX_TURNS"] - 1:
            response += " Your amazing adventure is coming to an end. GAME OVER – Thanks for playing!"
        
        # Extract vocabulary words from the response
        vocab_words = extract_vocabulary_from_text(response)
        
        return response, vocab_words
    
    def _get_fallback_segment(self, segment_number: int, theme: str) -> Dict[str, Any]:
        """Get fallback educational story segment when API is unavailable"""
        
        fallback_segments = {
            "magic_garden": {
                "story": "You discover a ✨magical garden✨ with singing flowers! A friendly butterfly 🦋 shows you sparkling treasures hidden among the colorful petals.",
                "choices": [
                    {"id": "A", "text": "Follow the butterfly 🦋", "is_correct": True},
                    {"id": "B", "text": "Listen to singing flowers 🌺", "is_correct": False},
                    {"id": "C", "text": "Explore the sparkling pond ✨", "is_correct": False},
                    {"id": "D", "text": "Look for treasure 💰", "is_correct": False}
                ],
                "challenge": {
                    "type": "word_completion",
                    "target_word": "garden",
                    "prompt": "Complete this word: g_rd_n (a place where flowers grow)",
                    "difficulty": "easy"
                }
            },
            "forest_adventure": {
                "story": "You enter a peaceful forest 🌲 where wise animals gather around a crystal stream. An owl 🦉 perches nearby, ready to share ancient secrets.",
                "choices": [
                    {"id": "A", "text": "Ask the owl for wisdom 🦉", "is_correct": True},
                    {"id": "B", "text": "Follow the crystal stream 💎", "is_correct": False},
                    {"id": "C", "text": "Meet the forest animals 🐿️", "is_correct": False},
                    {"id": "D", "text": "Sit by the water 🌊", "is_correct": False}
                ],
                "challenge": {
                    "type": "word_matching",
                    "target_word": "wisdom",
                    "prompt": "Match 'wisdom' with its meaning: knowledge, sadness, or hunger?",
                    "difficulty": "easy"
                }
            },
            "castle_mystery": {
                "story": "You approach a friendly castle 🏰 where colorful flags wave in the breeze. A kind knight 🛡️ welcomes you with a warm smile and offers to show you around.",
                "choices": [
                    {"id": "A", "text": "Explore the castle towers 🏰", "is_correct": True},
                    {"id": "B", "text": "Visit the royal garden 🌹", "is_correct": False},
                    {"id": "C", "text": "Meet the castle pets 🐕", "is_correct": False},
                    {"id": "D", "text": "Look at the flags 🏳️", "is_correct": False}
                ],
                "challenge": {
                    "type": "spelling",
                    "target_word": "castle",
                    "prompt": "Spell the word for a big, strong building where kings and queens live",
                    "difficulty": "easy"
                }
            }
        }
        
        # Select appropriate segment based on theme or use default
        if theme in fallback_segments:
            segment_data = fallback_segments[theme].copy()
        else:
            segment_data = fallback_segments["magic_garden"].copy()
        
        segment_data["segment_number"] = segment_number
        segment_data["theme"] = theme
        
        return segment_data
    
    def _get_fallback_hint(self, challenge_type: str) -> str:
        """Get fallback hint when API is unavailable"""
        
        hints = {
            "word_completion": "Try sounding out the missing letters! 🔤 Think about what sounds you hear in the word.",
            "word_matching": "Think about what the word means! 🤔 Which choice has the same meaning?",
            "spelling": "Say the word slowly and listen to each sound! 🎵 What letters make those sounds?"
        }
        
        return hints.get(challenge_type, "You're doing great! 🌟 Take your time and try your best!")


# Global Gemini client instance
gemini_client = GeminiClient()
