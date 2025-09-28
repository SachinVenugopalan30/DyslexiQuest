# Fallback responses when AI is unavailable

import random
from typing import Dict, List


# Story introductions by genre
FALLBACK_INTROS: Dict[str, List[str]] = {
    "fantasy": [
        "Welcome, brave adventurer! You stand before an ancient castle with glowing windows. A friendly wizard waves from a tower window. The enchanted forest whispers secrets in the wind. What do you want to explore first?",
        
        "Greetings, young hero! You've arrived in a magnificent kingdom where magic fills the air. A wise dragon lands nearby and offers to be your guide. Crystal caves sparkle in the distance. Where would you like to begin your quest?",
        
        "Hello, brave explorer! You find yourself in an enchanted garden where flowers sing beautiful melodies. A kind fairy appears and tells you about hidden treasures nearby. What magical discovery interests you most?"
    ],
    
    "adventure": [
        "Ahoy, treasure hunter! You've discovered an old map leading to a mysterious island. Your ship has just reached the sandy shore. Palm trees sway gently, and you can see a cave in the distance. Where do you want to start your expedition?",
        
        "Welcome, explorer! You stand at the entrance of ancient ruins filled with amazing secrets. Your guide points out interesting symbols carved in the stone walls. Adventure awaits around every corner! What catches your attention first?",
        
        "Greetings, adventurer! You've found a hidden valley with a sparkling waterfall and ancient bridges. Local villagers share stories of wonderful discoveries waiting to be made. Which path do you choose to explore?"
    ],
    
    "mystery": [
        "Hello, detective! You've arrived at a curious mansion where something mysterious has happened. The friendly butler greets you with a warm smile. There are interesting clues waiting to be found. Which room would you like to investigate first?",
        
        "Welcome, young investigator! You're at a charming library where books seem to move by themselves. The helpful librarian mentions that some volumes contain special puzzles. What would you like to examine first?",
        
        "Greetings, puzzle solver! You've discovered an old clock tower where time seems to work differently. Friendly townspeople mention strange but wonderful things happening here. What mystery would you like to solve first?"
    ],
    
    "sci-fi": [
        "Greetings, space explorer! Your spaceship has landed on a beautiful alien planet with purple skies and silver trees. Strange but friendly creatures watch you curiously from behind crystal rocks. Your scanner detects something interesting nearby. What do you want to discover first?",
        
        "Welcome, cosmic adventurer! You're aboard an amazing space station floating among colorful nebulae. Helpful robot friends offer to show you incredible technologies. The view of distant galaxies is magnificent! What would you like to explore?",
        
        "Hello, star traveler! You've arrived on a peaceful planet where everything glows softly with natural light. Kind alien scientists invite you to see their wonderful inventions. What fascinating discovery interests you most?"
    ]
}

# Continuing responses for various user actions
FALLBACK_RESPONSES: Dict[str, List[str]] = {
    "look_examine": [
        "You discover something magnificent! The ancient walls tell stories of brave adventurers. A mysterious symbol catches your eye. What would you like to examine more closely?",
        
        "Your keen eyes spot something interesting! There's a beautiful crystal that seems to illuminate the area. The treasure might be nearby. What's your next move?",
        
        "You observe your surroundings with wisdom! A hidden portal becomes visible when you look carefully. This expedition is full of surprises! Where do you want to explore?",
        
        "Amazing discovery! You find an enchanted book that glows when you touch it. The chronicle contains stories of other brave explorers. Would you like to read more?"
    ],
    
    "move_go": [
        "You courageously move forward! The path leads to an enchanted garden with singing flowers. A friendly guardian appears to help you. What do you want to ask them?",
        
        "You discover a sanctuary filled with glowing books. Each chronicle contains different stories. Which one interests you most?",
        
        "You transform your journey by choosing a new direction! Ahead lies a magnificent labyrinth made of silver and gold. Do you want to solve its riddle?",
        
        "Excellent choice! Your expedition brings you to a beautiful clearing where ancient trees share their wisdom. What would you like to learn from them?"
    ],
    
    "talk_speak": [
        "The character smiles warmly and shares their wisdom! They tell you about a hidden treasure that requires perseverance to find. They offer to help with your quest. Do you accept their guidance?",
        
        "Your friendly conversation reveals important clues! They mention an ancient expedition that discovered something wonderful nearby. Would you like to hear the complete chronicle?",
        
        "They greet you with enthusiasm! This guardian knows many secrets about the mysterious portal ahead. They're willing to illuminate the path for brave adventurers like you. What do you want to learn?",
        
        "What a delightful conversation! The wise character tells you about a magical sanctuary where courage and perseverance are rewarded. Would you like them to guide you there?"
    ],
    
    "use_take": [
        "Brilliant idea! The enchanted item responds to your touch and begins to glow. Ancient magic recognizes your courage and wisdom. Something magnificent happens! What do you want to try next?",
        
        "Excellent thinking! You discover the treasure has special powers that help brave adventurers. The guardian appears and congratulates your perseverance. What's your next adventure?",
        
        "What a clever choice! The mysterious object transforms and reveals a hidden message. This expedition is leading to amazing discoveries! How do you want to continue?",
        
        "Perfect! Your actions illuminate the true purpose of this ancient artifact. The wise guardian shares more secrets of this sanctuary. What would you like to explore further?"
    ],
    
    "general": [
        "What an excellent idea! Your creative thinking leads to an unexpected discovery. The mysterious puzzle begins to make sense. You're making great progress on this adventure! What's your next brilliant move?",
        
        "Your courage and wisdom guide you well! Something magnificent happens as a result of your actions. The ancient magic responds to your perseverance. How do you want to continue your expedition?",
        
        "Brilliant choice, young explorer! Your actions transform the situation in a wonderful way. The enchanted surroundings seem to approve of your decision. What would you like to discover next?",
        
        "Outstanding thinking! The guardian of this sanctuary appears and praises your wisdom. They offer to share the chronicle of other brave adventurers who succeeded here. Are you interested?",
        
        "Incredible! Your perseverance unlocks a hidden portal that leads to even more amazing discoveries. The ancient treasure responds to your courage. What magnificent adventure awaits you now?"
    ]
}

# Game ending responses
FALLBACK_ENDINGS: List[str] = [
    "What an incredible adventure you've completed! Your courage, wisdom, and perseverance have led to amazing discoveries. The treasure you've found is the knowledge and experience you've gained. The guardian of this realm thanks you for your wonderful journey.\n\nGAME OVER – Thanks for playing!",
    
    "Magnificent work, brave adventurer! You've shown great perseverance and discovered the most valuable treasure of all - the wisdom gained through your amazing expedition. All the characters you've met will remember your kindness and courage.\n\nGAME OVER – Thanks for playing!",
    
    "Outstanding adventure! Your journey through this enchanted realm has been filled with wonderful discoveries. The ancient chronicles will tell stories of your courage and wisdom for years to come. You've truly earned the title of Master Adventurer!\n\nGAME OVER – Thanks for playing!",
    
    "Brilliant exploration! You've transformed from a curious explorer into a wise adventurer. The sanctuary you've discovered will always welcome you back. Your perseverance and courage have illuminated the path for future adventurers.\n\nGAME OVER – Thanks for playing!"
]


class FallbackManager:
    """Manages fallback responses when AI is unavailable"""
    
    def get_intro(self, genre: str) -> str:
        """Get a random intro for the specified genre"""
        intros = FALLBACK_INTROS.get(genre, FALLBACK_INTROS["adventure"])
        return random.choice(intros)
    
    def get_response(self, user_input: str, turn: int) -> tuple[str, List[str]]:
        """Get a fallback response based on user input"""
        
        user_lower = user_input.lower()
        
        # Determine response category based on user input
        if any(word in user_lower for word in ["look", "examine", "see", "observe", "watch"]):
            responses = FALLBACK_RESPONSES["look_examine"]
        elif any(word in user_lower for word in ["go", "move", "walk", "travel", "north", "south", "east", "west", "forward", "back"]):
            responses = FALLBACK_RESPONSES["move_go"]
        elif any(word in user_lower for word in ["talk", "speak", "ask", "say", "tell", "conversation"]):
            responses = FALLBACK_RESPONSES["talk_speak"]
        elif any(word in user_lower for word in ["use", "take", "grab", "pick", "touch", "hold"]):
            responses = FALLBACK_RESPONSES["use_take"]
        else:
            responses = FALLBACK_RESPONSES["general"]
        
        # Select random response
        response = random.choice(responses)
        
        # Add ending if this is the final turn
        if turn >= 14:  # Second to last turn
            response += " Your amazing adventure is coming to an end soon!"
        elif turn >= 15:  # Final turn
            response = random.choice(FALLBACK_ENDINGS)
        
        # Extract vocabulary words (common adventure vocabulary)
        vocabulary_words = self._extract_fallback_vocabulary(response)
        
        return response, vocabulary_words
    
    def get_ending(self) -> str:
        """Get a random game ending"""
        return random.choice(FALLBACK_ENDINGS)
    
    def _extract_fallback_vocabulary(self, response: str) -> List[str]:
        """Extract vocabulary words from fallback responses"""
        
        # Common vocabulary words that might appear in responses
        vocab_candidates = [
            "adventure", "magnificent", "ancient", "treasure", "wisdom",
            "courage", "discover", "enchanted", "mysterious", "guardian",
            "sanctuary", "expedition", "chronicle", "perseverance", "transform",
            "illuminate", "portal", "crystal"
        ]
        
        found_words = []
        response_lower = response.lower()
        
        for word in vocab_candidates:
            if word in response_lower:
                found_words.append(word)
        
        # Return 1-2 words maximum
        return found_words[:2]


# Global fallback manager instance
fallback_manager = FallbackManager()
