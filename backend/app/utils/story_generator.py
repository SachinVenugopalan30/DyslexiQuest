# Story segment generator for dyslexia-friendly educational content

from typing import List, Dict, Optional, Any
import random
import uuid
from app.models.game import StorySegment, MultipleChoice, WordChallenge, VisualCue, Reward


class StorySegmentGenerator:
    """Generate educational story segments with progressive difficulty for children aged 5-10 with dyslexia"""
    
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
            'trees': '🌳',
            'cat': '🐱',
            'dog': '🐶',
            'bird': '🐦',
            'fish': '🐟',
            'home': '🏠',
            'tree': '🌳',
            'flower': '🌸',
            'help': '🤝',
            'friend': '👫',
            'safe': '🛡️'
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
                'name': 'Secret Island Adventure',
                'description': 'Explore a mysterious tropical island where you uncover hidden treasures, solve ancient puzzles, and help island friends',
                'themes': ['tropical island', 'hidden treasures', 'ancient puzzles', 'island wildlife', 'mysterious caves', 'friendly islanders', 'secret maps'],
                'vocabulary_focus': ['island', 'treasure', 'tropical', 'ancient', 'hidden', 'explore', 'discover']
            }
        }
    
    async def generate_educational_round(self, round_number: int, theme: str) -> StorySegment:
        """Generate an educational round with progressive difficulty"""
        
        # Determine difficulty based on round number
        if round_number <= 2:
            difficulty = "easy"
        elif round_number <= 5:
            difficulty = "intermediate"
        else:
            difficulty = "difficult"
        
        # LLM generation only
        from app.core.llm import gemini_client
        round_data = await gemini_client.generate_educational_round(
            round_number=round_number,
            theme=theme,
            difficulty=difficulty
        )
        return self._create_educational_segment(round_data, round_number)
    
    def _create_educational_segment(self, round_data: Dict[str, Any], round_number: int) -> StorySegment:
        """Create a StorySegment from educational round data"""
        
        # Create multiple choice options - only one is correct
        choices = []
        correct_index = round_data.get("correct", 0)
        
        # Debug: Log the round data to help diagnose issues
        print(f"DEBUG: Creating educational segment with correct_index={correct_index}, choices={round_data.get('choices', [])}")
        
        for i, choice_text in enumerate(round_data.get("choices", [])):
            is_correct = (i == correct_index)
            
            choice = MultipleChoice(
                id=f"choice_{i}",
                text=choice_text,
                is_correct=is_correct,
                feedback="Great job! 🌟" if is_correct else round_data.get("hint", "Try again! 🤔"),
                visual_cue=VisualCue(
                    icon=self._get_icon_for_text(choice_text),
                    description=f"Visual cue for {choice_text}",
                    position='before'
                ),
                difficulty_adjustment=0
            )
            choices.append(choice)
        
        # Create word challenge based on the educational content
        challenge_word = round_data.get("word", "help")
        
        word_challenge = WordChallenge(
            type='completion',  # Default to completion for educational rounds
            instruction=round_data.get("question", "What did you learn?"),
            word=challenge_word,
            correct_answer=challenge_word,
            hint=round_data.get("hint", "Sound it out slowly! 🔤"),
            visual_cue=VisualCue(
                icon=self.visual_icons.get(challenge_word, '✨'),
                description=f"Visual for {challenge_word}",
                position='before'
            ),
            difficulty_level=1 if round_data.get("difficulty") == "easy" else 2 if round_data.get("difficulty") == "intermediate" else 3
        )
        
        # Create visual cues for the story
        visual_cues = self._extract_visual_cues(round_data.get("story", ""))
        
        # Combine story text with question to show in AI response
        story_text = round_data.get("story", "Let's learn together! 📚")
        question_text = round_data.get("question", "What do you want to do next?")
        combined_text = f"{story_text}\n\n🤔 {question_text}"
        
        segment = StorySegment(
            id=str(uuid.uuid4()),
            text=combined_text,
            question=question_text,
            visual_cues=visual_cues,
            multiple_choices=choices,
            word_challenge=word_challenge,
            vocabulary_words=[challenge_word],
            difficulty_level=1 if round_data.get("difficulty") == "easy" else 2 if round_data.get("difficulty") == "intermediate" else 3,
            estimated_reading_time=self._estimate_reading_time(combined_text)
        )
        
        return segment
    
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
