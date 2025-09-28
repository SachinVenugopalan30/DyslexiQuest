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
            'surprise': '😮'
        }
        
        # Theme progression for different genres
        self.theme_progressions = {
            'fantasy': [
                'magic_garden', 'enchanted_forest', 'friendly_castle', 'crystal_cave',
                'talking_animals', 'magical_library', 'rainbow_bridge'
            ],
            'adventure': [
                'treasure_island', 'jungle_expedition', 'mountain_climb', 'ocean_discovery',
                'desert_oasis', 'ancient_ruins', 'hidden_village'
            ],
            'mystery': [
                'friendly_detective', 'missing_pet', 'secret_room', 'coded_message',
                'helpful_clues', 'solving_puzzle', 'happy_ending'
            ]
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
        
        # Remove hardcoded templates - now using pure LLM generation
        self.story_templates = {
                {
                    'text': "You find a magic key. 🗝️ It glows with blue light. The key feels warm in your hand.",
                    'choices': [
                        {'text': "Use the key on the door 🚪", 'correct': True, 'icon': '🚪'},
                        {'text': "Put the key in pocket 👛", 'correct': False, 'icon': '👛'},
                        {'text': "Look for more keys 🔍", 'correct': False, 'icon': '🔍'},
                        {'text': "Call for help 📢", 'correct': False, 'icon': '�'}
                    ],
                    'challenge': {'word': 'magic', 'type': 'spelling'},
                    'vocabulary': ['magic', 'glows', 'warm']
                },
                {
                    'text': "The door opens! 🚪✨ You see a bright garden. Flowers are singing happy songs.",
                    'choices': [
                        {'text': "Walk into the garden 🌸", 'correct': True, 'icon': '🌸'},
                        {'text': "Stay at the door 🚪", 'correct': False, 'icon': '🚪'},
                        {'text': "Wave at the flowers 👋", 'correct': False, 'icon': '👋'},
                        {'text': "Listen to the songs 🎵", 'correct': False, 'icon': '🎵'}
                    ],
                    'challenge': {'word': 'garden', 'type': 'matching'},
                    'vocabulary': ['bright', 'garden', 'singing']
                }
            ],
            'space': [
                {
                    'text': "Your rocket lands on Mars! 🚀 You see red rocks everywhere. A friendly alien waves hello.",
                    'choices': [
                        {'text': "Wave back at alien 👋", 'correct': True, 'icon': '👋'},
                        {'text': "Hide behind rocket 🙈", 'correct': False, 'icon': '🙈'},
                        {'text': "Take a photo 📸", 'correct': False, 'icon': '📸'},
                        {'text': "Say hello loudly 📢", 'correct': False, 'icon': '📢'}
                    ],
                    'challenge': {'word': 'rocket', 'type': 'completion'},
                    'vocabulary': ['rocket', 'Mars', 'alien']
                }
            ],
            'mystery': [
                {
                    'text': "You find a missing pet poster! 🐕 A friendly dog named Max is missing. There's a phone number to call.",
                    'choices': [
                        {'text': "Call the phone number 📞", 'correct': True, 'icon': '📞'},
                        {'text': "Look for paw prints 🐾", 'correct': True, 'icon': '🐾'},
                        {'text': "Ask people about Max 🗣️", 'correct': True, 'icon': '🗣️'},
                        {'text': "Make more posters 📋", 'correct': True, 'icon': '📋'}
                    ],
                    'challenge': {'word': 'missing', 'type': 'spelling'},
                    'vocabulary': ['missing', 'poster', 'friendly']
                },
                {
                    'text': "You hear barking nearby! 🐕 Someone points to the park. There are muddy footprints leading there.",
                    'choices': [
                        {'text': "Follow the footprints 👣", 'correct': True, 'icon': '👣'},
                        {'text': "Run to the park 🏃", 'correct': True, 'icon': '🏃'},
                        {'text': "Call Max's name 📢", 'correct': True, 'icon': '📢'},
                        {'text': "Look for more clues 🔍", 'correct': True, 'icon': '🔍'}
                    ],
                    'challenge': {'word': 'clues', 'type': 'matching'},
                    'vocabulary': ['barking', 'footprints', 'clues']
                }
            ]
        }
    
    async def generate_segment_with_llm(self, genre: str, difficulty: int, segment_index: int, previous_choices: Optional[List[str]] = None, story_context: Optional[List[str]] = None) -> StorySegment:
        """Generate a story segment using LLM for adaptive content"""
        
        # Get theme progression for the genre
        theme_list = self.theme_progressions.get(genre, self.theme_progressions['fantasy'])
        theme = theme_list[segment_index % len(theme_list)]
        
        # Try LLM generation first
        try:
            from app.core.llm import gemini_client
            llm_data = await gemini_client.generate_story_segment(
                segment_number=segment_index + 1,
                theme=theme,
                previous_choices=previous_choices,
                story_context=story_context
            )
            
            # Convert LLM response to StorySegment
            return self._create_segment_from_llm_data(llm_data, difficulty)
            
        except Exception as e:
            # Fall back to template system
            print(f"LLM generation failed, using template: {e}")
            return self.generate_segment(genre, difficulty, segment_index)
    
    def generate_segment(self, genre: str, difficulty: int, segment_index: int) -> StorySegment:
        """Generate a story segment based on genre and difficulty using templates"""
        
        if genre not in self.story_templates:
            genre = 'fantasy'  # Default fallback
        
        templates = self.story_templates[genre]
        if segment_index < len(templates):
            template = templates[segment_index]
        else:
            # Generate variations for longer sessions
            template = random.choice(templates)
        
        # Create multiple choice options - all choices are valid story paths
        choices = []
        for i, choice_data in enumerate(template['choices']):
            choice = MultipleChoice(
                id=f"choice_{i}",
                text=choice_data['text'],
                is_correct=True,  # All choices are valid story paths
                feedback=self._generate_feedback(True, difficulty),
                visual_cue=VisualCue(
                    icon=choice_data['icon'],
                    description=f"Visual cue for {choice_data['text']}",
                    position='before'
                ),
                difficulty_adjustment=0 if choice_data['correct'] else -1
            )
            choices.append(choice)
        
        # Create word challenge if specified
        word_challenge = None
        if 'challenge' in template:
            word_challenge = self._create_word_challenge(
                template['challenge'], difficulty
            )
        
        # Create visual cues for the main text
        visual_cues = self._extract_visual_cues(template['text'])
        
        segment = StorySegment(
            id=str(uuid.uuid4()),
            text=template['text'],
            visual_cues=visual_cues,
            multiple_choices=choices,
            word_challenge=word_challenge,
            vocabulary_words=template.get('vocabulary', []),
            difficulty_level=difficulty,
            estimated_reading_time=self._estimate_reading_time(template['text'])
        )
        
        return segment
    
    def _generate_feedback(self, is_correct: bool, difficulty: int) -> str:
        """Generate encouraging feedback for all choices"""
        encouraging_feedback = [
            "",
            "",
        ]
        return random.choice(encouraging_feedback)
    
    def _create_word_challenge(self, challenge_data: Dict, difficulty: int) -> WordChallenge:
        """Create a word challenge based on type and difficulty"""
        word = challenge_data['word']
        challenge_type = challenge_data['type']
        
        if challenge_type == 'spelling':
            # Create spelling challenge with missing letters
            missing_pos = len(word) // 2
            incomplete_word = word[:missing_pos] + '_' * (len(word) - missing_pos)
            
            return WordChallenge(
                type='spelling',
                instruction=f"Complete the word: {incomplete_word}",
                word=word,
                correct_answer=word,
                hint=f"This word starts with '{word[0]}' and has {len(word)} letters",
                visual_cue=VisualCue(
                    icon=self.visual_icons.get(word, '📝'),
                    description=f"Visual for {word}",
                    position='inline'
                ),
                difficulty_level=difficulty
            )
        
        elif challenge_type == 'matching':
            # Create matching challenge
            options = [word]
            # Add some similar but incorrect options
            wrong_options = ['garden', 'magic', 'castle', 'dragon', 'forest']
            options.extend([w for w in wrong_options if w != word][:2])
            random.shuffle(options)
            
            return WordChallenge(
                type='matching',
                instruction=f"Which word matches the picture? {self.visual_icons.get(word, '🖼️')}",
                word=word,
                options=options,
                correct_answer=word,
                hint="Look for the word that means the same as the picture!",
                visual_cue=VisualCue(
                    icon=self.visual_icons.get(word, '🖼️'),
                    description=f"Visual for {word}",
                    position='before'
                ),
                difficulty_level=difficulty
            )
        
        elif challenge_type == 'completion':
            # Create word completion challenge
            return WordChallenge(
                type='completion',
                instruction="What word completes this sentence? 'The space___ flew to Mars'",
                word=word,
                correct_answer=word,
                hint="Think about what travels through space!",
                visual_cue=VisualCue(
                    icon=self.visual_icons.get(word, '🚀'),
                    description=f"Visual for {word}",
                    position='inline'
                ),
                difficulty_level=difficulty
            )
        
        # Default fallback
        return WordChallenge(
            type='spelling',
            instruction=f"Spell this word: {word}",
            word=word,
            correct_answer=word,
            hint=f"Sound it out: {word}",
            difficulty_level=difficulty
        )
    
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
                difficulty_adjustment=0 if choice_data.get("is_correct", False) else -1
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
