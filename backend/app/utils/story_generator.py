# Story segment generator for dyslexia-friendly educational content

from typing import List, Dict, Optional, Any
import random
import uuid
from app.models.game import StorySegment, MultipleChoice, WordChallenge, VisualCue, Reward


class StorySegmentGenerator:
    """Generate educational story segments with dyslexia support and LLM integration"""
    
    def __init__(self):
        self.visual_icons = {
            'castle': '🏰',
            'forest': '🌲',
            'treasure': '💰',
            'magic': '✨',
            'dragon': '🐉',
            'knight': '🛡️',
            'princess': '👸',
            'wizard': '🧙‍♂️',
            'key': '🗝️',
            'door': '🚪',
            'book': '📚',
            'star': '⭐',
            'moon': '🌙',
            'sun': '☀️',
            'heart': '❤️',
            'happy': '😊',
            'thinking': '🤔',
            'surprise': '😮',
            'rocket': '🚀',
            'alien': '👽',
            'planet': '🪐',
            'space': '🌌',
            'detective': '🕵️',
            'clues': '🔍',
            'mystery': '❓',
            'animals': '🦌',
            'trees': '🌳'
        }
        
        # Adventure category descriptions for LLM prompts
        self.adventure_categories = {
            'forest': {
                'name': 'Forest Adventure',
                'description': 'An exciting journey through a magical forest filled with friendly animals, talking trees, and hidden treasures',
                'themes': ['woodland creatures', 'nature exploration', 'tree climbing', 'berry picking', 'animal friends', 'forest paths', 'cozy clearings'],
                'vocabulary_focus': ['forest', 'trees', 'animals', 'nature', 'explore', 'discover', 'adventure']
            },
            'space': {
                'name': 'Space Adventure', 
                'description': 'An amazing voyage through space visiting friendly planets, meeting kind aliens, and discovering cosmic wonders',
                'themes': ['space travel', 'friendly aliens', 'colorful planets', 'space stations', 'cosmic discoveries', 'rocket ships', 'star gazing'],
                'vocabulary_focus': ['space', 'planet', 'rocket', 'stars', 'explore', 'discover', 'galaxy']
            },
            'dungeon': {
                'name': 'Magical Dungeon Adventure',
                'description': 'A magical quest through a friendly dungeon filled with helpful creatures, puzzle rooms, and wonderful treasures',
                'themes': ['magical rooms', 'helpful guardians', 'puzzle solving', 'treasure hunting', 'magical creatures', 'glowing crystals', 'ancient wisdom'],
                'vocabulary_focus': ['magic', 'treasure', 'crystal', 'puzzle', 'explore', 'discover', 'mystery']
            },
            'mystery': {
                'name': 'Mystery Adventure',
                'description': 'A fun detective story where you help solve friendly mysteries, find missing things, and help your community',
                'themes': ['detective work', 'finding clues', 'helping others', 'solving puzzles', 'community helpers', 'missing pets', 'secret messages'],
                'vocabulary_focus': ['mystery', 'clues', 'detective', 'solve', 'help', 'discover', 'investigate']
            }
        }
        
        # Map old genre names to new categories for backward compatibility
        self.genre_mapping = {
            'fantasy': 'dungeon',  # Map fantasy to magical dungeon
            'adventure': 'forest',  # Map adventure to forest
            'sci-fi': 'space',     # Map sci-fi to space
            'mystery': 'mystery'   # Keep mystery as mystery
        }
    
    async def generate_segment_with_llm(self, genre: str, difficulty: int, segment_index: int, previous_choices: Optional[List[str]] = None, story_context: Optional[List[str]] = None) -> StorySegment:
        """Generate a story segment using LLM for adaptive content"""
        
        # Map old genre names to new categories
        mapped_genre = self.genre_mapping.get(genre, genre)
        if mapped_genre not in self.adventure_categories:
            mapped_genre = 'forest'  # Default fallback
        
        adventure_info = self.adventure_categories[mapped_genre]
        
        # Try LLM generation
        try:
            from app.core.llm import gemini_client
            llm_data = await gemini_client.generate_story_segment(
                segment_number=segment_index + 1,
                adventure_category=mapped_genre,
                adventure_info=adventure_info,
                previous_choices=previous_choices,
                story_context=story_context
            )
            
            # Convert LLM response to StorySegment
            return self._create_segment_from_llm_data(llm_data, difficulty)
            
        except Exception as e:
            # Create a simple fallback segment with detailed logging
            import traceback
            print(f"LLM generation failed for {mapped_genre} adventure segment {segment_index + 1}: {e}")
            print(f"Full error traceback: {traceback.format_exc()}")
            return self._create_fallback_segment(mapped_genre, difficulty, segment_index)
    
    def generate_segment(self, genre: str, difficulty: int, segment_index: int) -> StorySegment:
        """Generate a story segment - now always uses LLM or fallback"""
        
        # Map old genre names to new categories
        mapped_genre = self.genre_mapping.get(genre, genre)
        if mapped_genre not in self.adventure_categories:
            mapped_genre = 'forest'  # Default fallback
            
        return self._create_fallback_segment(mapped_genre, difficulty, segment_index)
    
    def _create_fallback_segment(self, genre: str, difficulty: int, segment_index: int) -> StorySegment:
        """Create a progressive fallback segment when LLM is unavailable"""
        
        adventure_info = self.adventure_categories.get(genre, self.adventure_categories['forest'])
        
        # Progressive fallback content based on genre and segment index
        fallback_content = {
            'forest': [
                {
                    'text': f"You enter a beautiful forest 🌲 filled with friendly animals! A wise owl 🦉 greets you warmly.",
                    'choices': [
                        "Talk to the owl 🦉",
                        "Explore deeper into forest 🌳", 
                        "Look for animal friends 🦌",
                        "Climb a tall tree 🧗‍♀️"
                    ]
                },
                {
                    'text': f"The wise owl 🦉 shares ancient forest secrets with you! It points toward a sparkling stream 💧 where magical berries grow.",
                    'choices': [
                        "Follow owl to stream 💧",
                        "Pick magical berries 🫐", 
                        "Ask owl more questions ❓",
                        "Thank owl and continue 🙏"
                    ]
                },
                {
                    'text': f"You discover a hidden grove 🌿 with glowing mushrooms! Friendly forest creatures 🐿️ invite you to join their circle.",
                    'choices': [
                        "Join the animal circle 🐿️",
                        "Touch glowing mushrooms ✨", 
                        "Dance with the creatures 💃",
                        "Share forest stories 📚"
                    ]
                }
            ],
            'space': [
                {
                    'text': f"Your spaceship lands on a colorful planet 🪐! Friendly aliens 👽 wave hello with big smiles.",
                    'choices': [
                        "Wave back at aliens 👋",
                        "Explore the planet 🚀",
                        "Take photos of stars ⭐",
                        "Visit the space station 🛸"
                    ]
                },
                {
                    'text': f"The friendly aliens 👽 show you their beautiful crystal city! They offer to take you on a tour of their amazing planet 🌟.",
                    'choices': [
                        "Take the planet tour 🌍",
                        "Visit the crystal city 💎",
                        "Learn alien language 🗣️",
                        "Share Earth stories 🌍"
                    ]
                }
            ],
            'dungeon': [
                {
                    'text': f"You discover a magical room ✨ with glowing crystals! A friendly guardian 🧙‍♂️ offers to help you.",
                    'choices': [
                        "Talk to the guardian 💬",
                        "Examine the crystals ✨",
                        "Look for treasure 💰",
                        "Solve the puzzle 🧩"
                    ]
                },
                {
                    'text': f"The guardian 🧙‍♂️ shows you a magical map! It reveals hidden treasures 💰 and secret passages throughout the friendly dungeon.",
                    'choices': [
                        "Follow the treasure map 🗺️",
                        "Explore secret passages 🚪",
                        "Learn guardian magic 🎩",
                        "Help organize treasures 📦"
                    ]
                }
            ],
            'mystery': [
                {
                    'text': f"You find an interesting clue 🔍! A helpful detective 🕵️ asks if you'd like to investigate together.",
                    'choices': [
                        "Work with detective 🤝",
                        "Search for more clues 🔍",
                        "Ask people questions 💬",
                        "Study the evidence 📝"
                    ]
                },
                {
                    'text': f"The detective 🕵️ shows you more clues! You discover the mystery is about a missing birthday cake 🎂 for the town celebration.",
                    'choices': [
                        "Search the bakery 🧁",
                        "Interview cake guests 👥",
                        "Follow cake crumbs 🍰",
                        "Check party supplies 🎈"
                    ]
                }
            ]
        }
        
        # Select content based on segment index
        content_list = fallback_content.get(genre, fallback_content['forest'])
        if segment_index < len(content_list):
            content = content_list[segment_index]
        else:
            # Loop back to earlier segments with variations for longer games
            content = content_list[segment_index % len(content_list)]
        
        # Create multiple choice options - all choices are valid story paths
        choices = []
        for i, choice_text in enumerate(content['choices']):
            choice = MultipleChoice(
                id=f"choice_{i}",
                text=choice_text,
                is_correct=True,  # All choices are valid story paths
                feedback=self._generate_feedback(True, difficulty),
                visual_cue=VisualCue(
                    icon=self._get_icon_for_text(choice_text),
                    description=f"Visual cue for {choice_text}",
                    position='before'
                ),
                difficulty_adjustment=0
            )
            choices.append(choice)
        
        # Create a simple word challenge
        vocab_words = adventure_info['vocabulary_focus']
        target_word = vocab_words[segment_index % len(vocab_words)]
        
        word_challenge = WordChallenge(
            type='spelling',
            instruction=f"Spell this adventure word: {target_word}",
            word=target_word,
            correct_answer=target_word,
            hint=f"This word is about your {adventure_info['name'].lower()}!",
            visual_cue=VisualCue(
                icon=self.visual_icons.get(target_word, '✨'),
                description=f"Visual for {target_word}",
                position='before'
            ),
            difficulty_level=difficulty
        )
        
        # Create visual cues for the main text
        visual_cues = self._extract_visual_cues(content['text'])
        
        segment = StorySegment(
            id=str(uuid.uuid4()),
            text=content['text'],
            visual_cues=visual_cues,
            multiple_choices=choices,
            word_challenge=word_challenge,
            vocabulary_words=vocab_words[:3],  # First 3 vocab words
            difficulty_level=difficulty,
            estimated_reading_time=self._estimate_reading_time(content['text'])
        )
        
        return segment
    
    def _generate_feedback(self, is_correct: bool, difficulty: int) -> str:
        """Generate encouraging feedback for all choices"""
        encouraging_feedback = [
            "Interesting choice! ⭐",
            "What a creative idea! 🌟",
            "That leads somewhere exciting! 👏",
            "Your adventure continues! 🎉",
            "Great thinking! 💫",
            "I like how you think! 🤔",
            "That's a brave decision! 🦸‍♀️",
            "Excellent choice! 💡",
            "Your story unfolds! ❤️",
            "What happens next? ✨"
        ]
        return random.choice(encouraging_feedback)
    
    def _extract_visual_cues(self, text: str) -> List[VisualCue]:
        """Extract visual cues from text with emojis"""
        cues = []
        for word, icon in self.visual_icons.items():
            if word in text.lower() or icon in text:
                cues.append(VisualCue(
                    icon=icon,
                    description=f"Visual cue for {word}",
                    position='inline'
                ))
        return cues
    
    def _estimate_reading_time(self, text: str) -> int:
        """Estimate reading time for dyslexic children (slower reading speed)"""
        words = len(text.split())
        # Assume 60-100 words per minute for children with dyslexia
        wpm = 80
        seconds = (words / wpm) * 60
        return max(10, int(seconds))  # Minimum 10 seconds
    
    def generate_reward(self, achievement_type: str) -> Reward:
        """Generate rewards for player achievements"""
        rewards = {
            'story_progress': Reward(
                type='star',
                name='Story Explorer',
                description='Your choice shapes the adventure!',
                icon='⭐',
                points=10
            ),
            'correct_choice': Reward(
                type='star',
                name='Bright Star',
                description='You made a great choice!',
                icon='⭐',
                points=10
            ),
            'challenge_complete': Reward(
                type='coin',
                name='Golden Coin',
                description='You solved the word puzzle!',
                icon='🪙',
                points=25
            ),
            'segment_complete': Reward(
                type='badge',
                name='Story Hero',
                description='You completed a story segment!',
                icon='🏆',
                points=50
            ),
            'session_complete': Reward(
                type='achievement',
                name='Reading Champion',
                description='You finished a whole reading session!',
                icon='👑',
                points=100
            )
        }
        
        return rewards.get(achievement_type, rewards['correct_choice'])
    
    def _create_segment_from_llm_data(self, llm_data: Dict[str, Any], difficulty: int) -> StorySegment:
        """Create a StorySegment from LLM generated data"""
        
        # Convert choices from LLM format to MultipleChoice objects
        choices = []
        for choice_data in llm_data.get("choices", []):
            choice = MultipleChoice(
                id=choice_data.get("id", f"choice_{len(choices)}"),
                text=choice_data.get("text", "Continue exploring"),
                is_correct=True,  # All choices are valid story paths
                feedback=self._generate_feedback(True, difficulty),
                visual_cue=VisualCue(
                    icon=self._get_icon_for_text(choice_data.get("text", "")),
                    description=f"Visual cue for {choice_data.get('text', 'choice')}",
                    position='before'
                ),
                difficulty_adjustment=0
            )
            choices.append(choice)
        
        # Create word challenge if provided by LLM
        word_challenge = None
        challenge_data = llm_data.get("challenge")
        if challenge_data:
            challenge_word = challenge_data.get("target_word", "magic")
            challenge_type = challenge_data.get("type", "word_completion")
            
            if challenge_type == "word_completion":
                # Create completion challenge
                missing_letters = len(challenge_word) // 2
                incomplete = challenge_word[:-missing_letters] + '_' * missing_letters
                instruction = f"Complete this word: {incomplete}"
            elif challenge_type == "word_matching":
                instruction = challenge_data.get("prompt", f"What does '{challenge_word}' mean?")
            else:  # spelling
                instruction = challenge_data.get("prompt", f"Spell the word: {challenge_word}")
            
            # Convert string difficulty to int
            difficulty_str = challenge_data.get("difficulty", "easy")
            difficulty_int = {"easy": 1, "medium": 2, "hard": 3}.get(difficulty_str, 1)
            
            word_challenge = WordChallenge(
                type=challenge_type,
                instruction=instruction,
                word=challenge_word,
                correct_answer=challenge_word,
                hint=challenge_data.get("hint", f"Think about the word '{challenge_word}'"),
                visual_cue=VisualCue(
                    icon=self._get_icon_for_text(challenge_word),
                    description=f"Visual for {challenge_word}",
                    position='before'
                ),
                difficulty_level=difficulty_int
            )
        
        # Extract visual cues from story text
        visual_cues = self._extract_visual_cues(llm_data.get("story", ""))
        
        # Create the segment
        segment = StorySegment(
            id=str(uuid.uuid4()),
            text=llm_data.get("story", "You continue your adventure..."),
            multiple_choices=choices,
            word_challenge=word_challenge,
            visual_cues=visual_cues,
            difficulty_level=difficulty,
            estimated_reading_time=self._estimate_reading_time(llm_data.get("story", "")),
            accessibility_features={
                'high_contrast': True,
                'text_to_speech': True,
                'dyslexia_friendly_font': True,
                'visual_cues': True
            }
        )
        
        return segment
    
    def _get_icon_for_text(self, text: str) -> str:
        """Get an appropriate icon for given text"""
        text_lower = text.lower()
        
        for keyword, icon in self.visual_icons.items():
            if keyword in text_lower:
                return icon
        
        # Default icons based on common words
        if any(word in text_lower for word in ['go', 'walk', 'move']):
            return '👣'
        elif any(word in text_lower for word in ['look', 'see', 'watch']):
            return '👀'
        elif any(word in text_lower for word in ['talk', 'speak', 'ask']):
            return '💬'
        elif any(word in text_lower for word in ['help', 'assist']):
            return '🤝'
        else:
            return '✨'  # Default magical icon


# Global generator instance
story_generator = StorySegmentGenerator()
