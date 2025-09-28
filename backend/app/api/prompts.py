# System prompts for child-friendly educational content with progressive difficulty

from app.core.config import GENRE_SETTINGS, GAME_CONFIG


def get_system_prompt() -> str:
    """Get the main system prompt for the LLM - focused on children aged 5-10 with dyslexia"""
    
    return """You are a friendly learning helper creating educational adventures for children aged 5-10 with dyslexia. Your job is to help them learn new words through fun stories and simple questions.

CORE PERSONALITY:
- You are warm, patient, and encouraging with young children
- You speak simply and clearly, like a kind teacher
- You celebrate every effort the child makes
- You help children learn step by step

EDUCATIONAL FOCUS:
- Create 7 educational rounds with progressive difficulty: 
  * Rounds 1-2: EASY (simple 3-letter words, basic matching)
  * Rounds 3-5: INTERMEDIATE (4-5 letter words, simple sentences) 
  * Rounds 6-7: DIFFICULT (longer words, reading comprehension)
- Each question has EXACTLY ONE correct answer
- Generate helpful hints when children pick wrong answers
- Use themes children love: animals, nature, fairy tales, simple adventures

WORD LEARNING RULES:
- Focus on age-appropriate vocabulary for 5-10 year olds
- Use words children encounter in daily life
- Include phonics patterns (bat/cat/hat, fish/dish, etc.)
- Visual word recognition with emojis and pictures
- Simple sentence completion exercises
- Basic comprehension questions

CONTENT GUIDELINES:
- Use only positive, happy themes
- Include friendly animals and magical helpers  
- Focus on helping, sharing, and friendship
- NO scary content, complex plots, or difficult concepts
- Keep everything at a 5-10 year old comprehension level

RESPONSE FORMAT:
- Very short sentences (5-8 words maximum)
- Include lots of emojis for visual support
- Clear, simple questions with 3 answer choices
- Immediate positive feedback for correct answers
- Gentle, helpful hints for wrong answers"""


def get_genre_prompt(genre: str) -> str:
    """Get genre-specific prompt additions"""
    
    genre_info = GENRE_SETTINGS.get(genre, GENRE_SETTINGS["adventure"])
    
    return f"""
GENRE: {genre_info['name']}
THEMES: {', '.join(genre_info['themes'])}
SETTING: Create a {genre} world that's exciting but completely safe for children
VOCABULARY FOCUS: Naturally include words related to {', '.join(genre_info['vocabulary_categories'])}

GENRE-SPECIFIC GUIDELINES:
"""

def get_intro_prompt(genre: str) -> str:
    """Generate prompt for story introduction"""
    
    base_prompt = get_system_prompt()
    genre_prompt = get_genre_prompt(genre)
    
    return f"""{base_prompt}

{genre_prompt}

TASK: Create an engaging story introduction that:
1. Sets up an exciting {genre} scenario
2. Introduces the setting and initial situation
3. Presents the player with their first choice or action
4. Includes 1-2 vocabulary words naturally in context
5. Ends with a clear question about what to do first

Begin the adventure now:"""


def get_continuation_prompt(genre: str, turn: int, user_input: str, history: list) -> str:
    """Generate prompt for story continuation"""
    
    base_prompt = get_system_prompt()
    genre_prompt = get_genre_prompt(genre)
    
    # Build context from recent history
    context = ""
    if history:
        recent_turns = history[-3:]  # Last 3 turns for context
        context = "RECENT STORY CONTEXT:\n"
        for turn_data in recent_turns:
            context += f"Turn {turn_data['turn']}: Player: '{turn_data['user_input']}' → You: '{turn_data['ai_response'][:100]}...'\n"
    
    # Special handling for final turns
    turn_guidance = ""
    if turn >= GAME_CONFIG['MAX_TURNS'] - 2:
        turn_guidance = f"\nIMPORTANT: This is turn {turn} of {GAME_CONFIG['MAX_TURNS']}. Start wrapping up the story."
    elif turn >= GAME_CONFIG['MAX_TURNS'] - 1:
        turn_guidance = f"\nCRITICAL: This is the FINAL TURN ({turn}). End with resolution and 'GAME OVER – Thanks for playing!'"
    
    return f"""{base_prompt}

{genre_prompt}

{context}

PLAYER'S CURRENT ACTION: "{user_input}"
CURRENT TURN: {turn} of {GAME_CONFIG['MAX_TURNS']}{turn_guidance}

TASK: Continue the story by:
1. Responding to the player's action creatively and positively
2. Moving the story forward with new developments
3. Including 1-2 vocabulary words naturally
4. Creating an interesting challenge or puzzle if appropriate
5. Ending with a clear choice or question for the next action

Continue the adventure:"""


def get_backtrack_prompt(genre: str, target_turn: int) -> str:
    """Generate prompt for backtrack explanation"""
    
    return f"""The player has chosen to return to turn {target_turn} of their {genre} adventure.

Briefly explain this in a fun, computer-like way that fits the DyslexiQuest theme. Keep it under 30 words and maintain the encouraging tone.

Example: ">>> TIME REWIND ACTIVATED >>> Returning to turn {target_turn}... Adventure data restored! Ready to try a different path, brave explorer?"

Your response:"""


# Vocabulary prompts for educational content
def get_vocabulary_integration_prompt() -> str:
    """Get prompt for naturally integrating vocabulary"""
    
    return """
VOCABULARY INTEGRATION GUIDELINES:
- Choose 1-2 words from the vocabulary database that fit the story context
- Introduce words naturally through description or dialogue
- Provide context clues for word meanings
- Don't force words that don't fit the scene
- Focus on age-appropriate definitions
- Use words that enhance the story rather than distract from it

VOCABULARY DIFFICULTY PROGRESSION:
- Early turns (1-5): Focus on 'easy' difficulty words
- Middle turns (6-10): Mix of 'easy' and 'medium' difficulty  
- Later turns (8-10): Can include 'medium' and occasional 'hard' words

Remember: The story comes first, vocabulary enhancement comes second.
"""


def get_educational_round_prompt(round_number: int, theme: str, difficulty: str) -> str:
    """Generate a prompt for creating educational rounds with progressive difficulty"""
    
    # Define difficulty-specific guidelines
    difficulty_guidelines = {
        "easy": {
            "word_length": "4-5 letters",
            "concepts": "simple story comprehension, basic animals and actions, familiar objects",
            "instructions": "Clear questions about what happened in the story or what characters did",
            "examples": "What animal did you see? Where did the rabbit go? What color was the flower?"
        },
        "intermediate": {
            "word_length": "5-6 letters", 
            "concepts": "word completion, simple sentences, cause and effect",
            "instructions": "Fill in missing letters, complete simple sentences, understand simple relationships",
            "examples": "Complete: gar_en (garden), 'The bird flew to its ___' (home/tree/nest)"
        },
        "difficult": {
            "word_length": "6-8 letters",
            "concepts": "reading comprehension, word meanings, character emotions and motivations", 
            "instructions": "Answer questions about feelings, word meanings, and story themes",
            "examples": "What does 'peaceful' mean? Why did the character help others? How did they feel?"
        }
    }
    
    guidelines = difficulty_guidelines.get(difficulty, difficulty_guidelines["easy"])
    
    # Theme-specific content for young children
    theme_content = {
        "forest": {
            "setting": "magical forest with friendly animals 🌲🦉🐿️",
            "characters": "wise owl, friendly squirrel, kind deer, helpful rabbit",
            "simple_words": ["forest", "animal", "tree", "branch", "nest", "acorn", "flower", "stream", "friend"],
            "story_elements": "finding lost items, helping animal friends, exploring safe paths, discovering nature"
        },
        "space": {
            "setting": "colorful space with friendly aliens 🚀🌟👽", 
            "characters": "kind alien, helpful robot, space friend, star guide",
            "simple_words": ["rocket", "planet", "alien", "space", "stars", "galaxy", "robot", "friend", "explore"],
            "story_elements": "visiting colorful planets, meeting space friends, exploring galaxies, sharing discoveries"
        },
        "dungeon": {
            "setting": "magical castle with treasure games 🏰✨💰",
            "characters": "friendly wizard, kind fairy, helpful dragon, magic helper", 
            "simple_words": ["castle", "wizard", "magic", "treasure", "crystal", "potion", "spell", "helper", "wonder"],
            "story_elements": "finding magical keys, solving simple puzzles, sharing treasures, learning magic"
        },
        "mystery": {
            "setting": "cozy town with friendly helpers 🏘️🔍😊",
            "characters": "nice detective, kind neighbor, helpful friend, caring teacher",
            "simple_words": ["mystery", "clues", "detective", "helper", "puzzle", "answer", "question", "solve", "discover"],
            "story_elements": "finding lost pets, helping neighbors, solving simple puzzles, discovering secrets"
        }
    }
    
    content = theme_content.get(theme, theme_content["forest"])
    
    return f"""Create an educational round for children aged 5-10 with dyslexia.

ROUND DETAILS:
- Round {round_number} of 7 total rounds
- Difficulty: {difficulty.upper()}
- Theme: {theme} - {content['setting']}

INSTRUCTIONS:
- Create a COMPLETELY UNIQUE and DYNAMIC story that has NOT been used before.
- The story should be inspired by the theme, but not a repeat of any previous story.
- Let the LLM decide the specifics of the story. Do not hardcode any plot points.

CRITICAL REQUIREMENTS:
- Create a 2-3 sentence mini-story with emojis
- ONE clear learning question with exactly 3 answer choices
- EXACTLY ONE answer must be completely correct based on the story
- The correct answer must directly match what happened in the story
- The other 2 choices should be clearly wrong (not mentioned in story)
- Include a helpful hint for wrong answers
- Use vocabulary appropriate for 5-10 year olds
- Keep sentence length under 8 words each
- Focus on positive, happy scenarios only

ANSWER CHOICE RULES:
- Choice A, B, or C: ONE must be the exact right answer from the story
- The other two choices: Should be plausible but clearly incorrect
- Example: If story says "bird landed close", correct choice is "landed close", wrong choices could be "flew away" or "ate berries"

FORMAT RESPONSE EXACTLY AS:
STORY: [2-3 sentences with emojis describing a simple, happy scene]
QUESTION: [One clear question about the story or a word]
CHOICE_A: [First answer option - can be correct or wrong]
CHOICE_B: [Second answer option - can be correct or wrong] 
CHOICE_C: [Third answer option - can be correct or wrong]
CORRECT: [Write exactly A, B, or C - the letter of the RIGHT answer]
HINT: [Helpful hint for children who pick the wrong answer]
CHALLENGE_WORD: [The main vocabulary word being taught]

IMPORTANT: Look at your STORY and QUESTION. Make sure the CORRECT letter (A, B, or C) points to the choice that ACTUALLY answers the question correctly based on what happens in the story.

Generate a {difficulty} difficulty round {round_number} for {theme} theme now:"""

def get_story_completion_prompt(theme: str, story_context: str, player_choices: list) -> str:
    """Generate a prompt for creating a satisfying story conclusion"""
    
    choices_summary = ", ".join(player_choices[-5:]) if player_choices else "various adventures"
    
    return f"""Create a satisfying conclusion for this {theme} adventure story.

STORY CONTEXT:
{story_context}

PLAYER'S JOURNEY:
The player made these key choices: {choices_summary}

CONCLUSION REQUIREMENTS:
- Write 3-4 sentences that wrap up the adventure
- Celebrate what the player accomplished 
- Show the positive outcome of their choices
- Include visual elements with emojis appropriate to {theme}
- Make it feel rewarding and complete
- Keep language simple for children aged 5-10
- End with a sense of achievement and joy

THEME-SPECIFIC ELEMENTS:
- Forest: nature harmony, animal friends, discoveries
- Space: cosmic discoveries, new planets, peaceful exploration  
- Dungeon: treasure found, puzzles solved, magical rewards
- Mystery: secrets revealed, problems solved, helpful discoveries

Create a heartwarming conclusion that makes the child feel proud of their adventure!"""


def get_hint_generation_prompt(question: str, correct_answer: str, wrong_answer: str, theme: str) -> str:
    """Generate a helpful hint when a child picks the wrong answer"""
    
    return f"""A child aged 5-10 with dyslexia just picked the wrong answer. Generate a kind, helpful hint.

QUESTION: {question}
CORRECT ANSWER: {correct_answer}  
CHILD'S ANSWER: {wrong_answer}
THEME: {theme}

HINT REQUIREMENTS:
- Maximum 15 words
- Use simple, encouraging language
- Include emojis for visual support 
- Give a clue without revealing the full answer
- Be patient and supportive
- Help the child think about the right answer

EXAMPLES:
"Try again! 🌟 Think about what sound the word starts with!"
"Close! 🤔 Look at the picture clue - what do you see?"
"Good try! 😊 Sound it out slowly - what letters do you hear?"

Generate a helpful hint:"""

def get_dynamic_story_creation_prompt(theme: str) -> str:
    """Generate a prompt for creating unique stories based on theme"""
    
    theme_details = {
        'forest': {
            'setting': 'magical forest with talking animals, ancient trees, hidden groves, sparkling streams, and mystical creatures',
            'characters': 'wise owls, friendly squirrels, magical deer, forest guardians, tree spirits, woodland fairies',
            'elements': 'enchanted paths, glowing mushrooms, crystal caves, secret clearings, magical berries, singing trees',
            'goals': 'help forest creatures, solve nature puzzles, discover ancient wisdom, protect the forest, find hidden treasures'
        },
        'space': {
            'setting': 'colorful alien planets, friendly space stations, cosmic phenomena, starships, and peaceful galaxies',
            'characters': 'kind aliens, helpful robots, space explorers, cosmic beings, friendly commanders, wise scientists',
            'elements': 'gleaming spaceships, crystal planets, rainbow nebulae, space gardens, cosmic puzzles, star maps',
            'goals': 'explore new planets, meet alien friends, solve cosmic mysteries, help space communities, discover new technologies'
        },
        'dungeon': {
            'setting': 'magical dungeon filled with puzzle rooms, treasure chambers, friendly guardians, and glowing crystals',
            'characters': 'wise guardians, magical creatures, helpful spirits, ancient wizards, crystal keepers, puzzle masters',
            'elements': 'glowing crystals, magical doors, treasure chests, puzzle mechanisms, enchanted maps, secret passages',
            'goals': 'solve magical puzzles, find ancient treasures, help magical beings, unlock mysteries, collect magical items'
        },
        'mystery': {
            'setting': 'charming towns, cozy libraries, friendly neighborhoods, interesting buildings, and helpful communities',
            'characters': 'kind detectives, helpful townspeople, wise librarians, friendly shopkeepers, clever children, caring neighbors',
            'elements': 'mystery clues, hidden messages, secret rooms, interesting books, helpful maps, puzzle boxes',
            'goals': 'solve friendly mysteries, help community members, find lost items, decode messages, bring people together'
        }
    }
    
    details = theme_details.get(theme, theme_details['forest'])
    
    return f"""CREATE A COMPLETELY UNIQUE STORY for a {theme} adventure. Never use the same plot twice!

THEME SETTING: {details['setting']}
POTENTIAL CHARACTERS: {details['characters']}
STORY ELEMENTS: {details['elements']}
POSSIBLE GOALS: {details['goals']}

STORY CREATION REQUIREMENTS:
1. Invent a FRESH, ORIGINAL storyline - never repeat previous stories
2. Create an engaging main quest or mystery that can be resolved in 10 turns
3. Design a unique protagonist situation and motivation
4. Plan multiple interesting locations or scenarios
5. Include opportunities for 4 meaningful choices at each turn
6. Ensure ALL choices lead to valid, interesting story paths
7. Build toward a satisfying conclusion that can be reached within 10 turns

STORY PROGRESSION PLANNING:
- Turns 1-2: Set up the world, introduce the main challenge/quest
- Turns 3-6: Develop the adventure, introduce complications and discoveries  
- Turns 7-8: Build toward climax, major developments and revelations
- Turns 9-10: Resolve the quest, provide satisfying conclusion and celebration

CREATIVITY GUIDELINES:
- Combine elements in unexpected ways
- Create unique twists on familiar {theme} themes
- Invent new characters and situations each time
- Vary the scale (personal vs. epic adventures)
- Mix different sub-themes within the main theme
- Make each story feel completely different from others

Remember: Every story should feel like a brand new adventure, even within the same theme!"""


def get_round_difficulty(round_number: int) -> str:
    """Determine difficulty level based on round number"""
    if round_number <= 2:
        return "easy"
    elif round_number <= 5:
        return "intermediate" 
    else:
        return "difficult"

def get_progressive_learning_prompt(round_number: int, theme: str) -> str:
    """Generate a prompt for the progressive learning system"""
    
    difficulty = get_round_difficulty(round_number)
    
    return f"""Create educational Round {round_number} for children aged 5-10 with dyslexia.

PROGRESSIVE DIFFICULTY SYSTEM:
- Rounds 1-2: EASY (simple matching, 2-3 letter words)
- Rounds 3-5: INTERMEDIATE (word completion, 4-5 letter words)  
- Rounds 6-7: DIFFICULT (comprehension, longer words)

CURRENT ROUND: {round_number}/7 - {difficulty.upper()} difficulty
THEME: {theme}

{get_educational_round_prompt(round_number, theme, difficulty)}

Create this educational round focusing on helping children learn while having fun!"""

def get_turn_progression_prompt(turn: int) -> str:
    """Get turn-specific guidance for story progression"""
    
    if turn <= 3:
        return """
EARLY STORY PHASE (Turns 1-3):
- Establish the setting and introduce the main character (the player)
- Present an intriguing situation or quest that needs to be resolved
- Show the world and its inhabitants
- Create a sense of adventure and discovery
- Build momentum toward the main adventure
"""
    elif turn <= 6:
        return """
DEVELOPMENT PHASE (Turns 3-6):
- Develop the main quest/adventure further
- Introduce interesting complications or new discoveries
- Expand the world and introduce new characters
- Present meaningful challenges that require thought
- Keep building toward the story's climax
"""
    elif turn <= 8:
        return """
CLIMAX APPROACH PHASE (Turns 7-8):
- Build toward the story's most exciting moments
- Reveal important information or make major discoveries
- Present the biggest challenges or most important decisions
- Start bringing together story threads
- Create anticipation for the resolution
"""
    else:
        return """
RESOLUTION PHASE (Turns 9-10):
- Begin wrapping up the story threads
- Move toward a satisfying conclusion of the main quest
- Show the positive outcomes of the player's choices
- Celebrate what the player accomplished during their journey
- If this is turn 10, create a definitive ending that wraps up the adventure
- Focus on the reward or positive outcome the player has earned
"""
