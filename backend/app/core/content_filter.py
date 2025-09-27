# Content filtering for child safety

import re
import logging
from typing import List, Optional
from app.core.config import CONTENT_FILTER_KEYWORDS

logger = logging.getLogger(__name__)


class ContentFilter:
    """Content safety filter for ensuring child-appropriate responses"""
    
    def __init__(self):
        # Keywords that should trigger content filtering
        self.blocked_keywords = set(CONTENT_FILTER_KEYWORDS)
        
        # Patterns for inappropriate content
        self.blocked_patterns = [
            r'\b(kill|death|die|dead)\b',
            r'\b(weapon|gun|knife|sword|fight)\b', 
            r'\b(scary|horror|frightening|terrifying)\b',
            r'\b(violence|violent|attack|battle)\b',
            r'\b(dark|evil|demon|monster|ghost)\b',
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.blocked_patterns]
    
    def is_safe_content(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Check if content is safe for children
        Returns (is_safe, reason_if_not_safe)
        """
        if not text or not isinstance(text, str):
            return False, "Empty or invalid content"
        
        text_lower = text.lower()
        
        # Check for blocked keywords
        for keyword in self.blocked_keywords:
            if keyword in text_lower:
                logger.warning(f"Content blocked for keyword: {keyword}")
                return False, f"Contains inappropriate keyword: {keyword}"
        
        # Check regex patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                logger.warning(f"Content blocked for pattern match")
                return False, "Contains inappropriate content pattern"
        
        # Check for excessive capitalization (shouting)
        if self._is_excessive_caps(text):
            return False, "Excessive capitalization detected"
        
        # Check length limits
        if len(text) < 5:
            return False, "Content too short"
        
        if len(text) > 1000:
            return False, "Content too long"
        
        return True, None
    
    def sanitize_input(self, user_input: str) -> str:
        """Clean and sanitize user input"""
        if not user_input:
            return ""
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', user_input.strip())
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>{}[\]\\]', '', sanitized)
        
        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        
        return sanitized
    
    def get_safe_alternative(self, unsafe_content: str) -> str:
        """Generate a safe alternative response when content is filtered"""
        
        safe_alternatives = [
            "Let's try a different approach! How about exploring something new in our adventure?",
            "That's quite creative! Let's think of a friendlier way to continue our story.",
            "Interesting idea! Can you try describing what you want to do in a different way?",
            "I love your imagination! Let's keep our adventure fun and safe for everyone.",
            "Great thinking! How about we try something else that fits our magical world?",
        ]
        
        import random
        return random.choice(safe_alternatives)
    
    def _is_excessive_caps(self, text: str) -> bool:
        """Check if text has excessive capitalization"""
        if len(text) < 10:
            return False
        
        uppercase_count = sum(1 for char in text if char.isupper())
        total_letters = sum(1 for char in text if char.isalpha())
        
        if total_letters == 0:
            return False
        
        caps_percentage = uppercase_count / total_letters
        return caps_percentage > 0.7  # More than 70% caps
    
    def validate_response_safety(self, ai_response: str) -> tuple[bool, str]:
        """Validate that AI response is safe for children"""
        
        is_safe, reason = self.is_safe_content(ai_response)
        
        if not is_safe:
            logger.warning(f"AI response filtered: {reason}")
            safe_response = self.get_safe_alternative(ai_response)
            return False, safe_response
        
        return True, ai_response
    
    def check_vocabulary_appropriateness(self, words: List[str]) -> List[str]:
        """Filter vocabulary words to ensure they're appropriate"""
        
        safe_words = []
        
        for word in words:
            is_safe, _ = self.is_safe_content(word)
            if is_safe and len(word) >= 3:  # Minimum word length
                safe_words.append(word)
        
        return safe_words


# Global content filter instance  
content_filter = ContentFilter()


def validate_user_input(user_input: str) -> tuple[bool, str]:
    """Validate and sanitize user input"""
    
    if not user_input or not user_input.strip():
        return False, "Please enter something to continue your adventure!"
    
    # Sanitize the input
    clean_input = content_filter.sanitize_input(user_input)
    
    if not clean_input:
        return False, "Please try a different way to describe what you want to do."
    
    # Check content safety
    is_safe, reason = content_filter.is_safe_content(clean_input)
    
    if not is_safe:
        safe_message = content_filter.get_safe_alternative(clean_input)
        return False, safe_message
    
    return True, clean_input


def validate_ai_response(ai_response: str, vocabulary_words: List[str]) -> tuple[str, List[str]]:
    """Validate and filter AI response and vocabulary"""
    
    # Validate main response
    is_safe, safe_response = content_filter.validate_response_safety(ai_response)
    
    # Filter vocabulary words
    safe_vocab = content_filter.check_vocabulary_appropriateness(vocabulary_words)
    
    return safe_response, safe_vocab
