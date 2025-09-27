# Vocabulary database for the text adventure game

from typing import Dict
from app.models.game import VocabularyWord

# Complete vocabulary database for the game
VOCABULARY_DATABASE: Dict[str, VocabularyWord] = {
    'adventure': VocabularyWord(
        word='adventure',
        definition='An exciting or dangerous experience or journey',
        difficulty='easy',
        category='general',
        example='Going on an adventure through the forest was thrilling!',
        synonyms=['journey', 'expedition', 'quest'],
        phonetic='/ədˈven(t)SHər/'
    ),
    'mysterious': VocabularyWord(
        word='mysterious',
        definition='Strange, unknown, or difficult to understand',
        difficulty='medium',
        category='descriptive',
        example='The mysterious door had no handle or keyhole.',
        synonyms=['puzzling', 'unknown', 'secretive'],
        phonetic='/məˈstirēəs/'
    ),
    'courage': VocabularyWord(
        word='courage',
        definition='The ability to do something brave or difficult',
        difficulty='medium',
        category='emotion',
        example='It took courage to enter the dark cave.',
        synonyms=['bravery', 'boldness', 'valor'],
        phonetic='/ˈkərij/'
    ),
    'ancient': VocabularyWord(
        word='ancient',
        definition='Very old, from long ago in history',
        difficulty='easy',
        category='time',
        example='The ancient castle was built hundreds of years ago.',
        synonyms=['old', 'historic', 'aged'],
        phonetic='/ˈān(t)SHənt/'
    ),
    'discover': VocabularyWord(
        word='discover',
        definition='To find something for the first time',
        difficulty='easy',
        category='action',
        example='We might discover treasure in the hidden room.',
        synonyms=['find', 'uncover', 'reveal'],
        phonetic='/dəˈskəvər/'
    ),
    'enchanted': VocabularyWord(
        word='enchanted',
        definition='Having magical powers or under a magic spell',
        difficulty='medium',
        category='magic',
        example='The enchanted sword glowed with blue light.',
        synonyms=['magical', 'bewitched', 'spellbound'],
        phonetic='/ənˈCHan(t)əd/'
    ),
    'riddle': VocabularyWord(
        word='riddle',
        definition='A puzzle or question that needs clever thinking to solve',
        difficulty='medium',
        category='puzzle',
        example='The sphinx asked a difficult riddle.',
        synonyms=['puzzle', 'mystery', 'brain teaser'],
        phonetic='/ˈridl/'
    ),
    'treasure': VocabularyWord(
        word='treasure',
        definition='Valuable things like gold, jewels, or precious objects',
        difficulty='easy',
        category='objects',
        example='The pirates buried their treasure on the island.',
        synonyms=['riches', 'valuables', 'wealth'],
        phonetic='/ˈtreSHər/'
    ),
    'wisdom': VocabularyWord(
        word='wisdom',
        definition='Knowledge and good judgment gained from experience',
        difficulty='hard',
        category='abstract',
        example='The old wizard shared his wisdom with young adventurers.',
        synonyms=['knowledge', 'insight', 'understanding'],
        phonetic='/ˈwizdəm/'
    ),
    'labyrinth': VocabularyWord(
        word='labyrinth',
        definition='A complicated network of paths; a maze',
        difficulty='hard',
        category='places',
        example='Getting lost in the labyrinth was scary but exciting.',
        synonyms=['maze', 'network', 'puzzle'],
        phonetic='/ˈlabəˌrinTH/'
    ),
    'crystal': VocabularyWord(
        word='crystal',
        definition='A clear, transparent mineral that sparkles',
        difficulty='easy',
        category='objects',
        example='The crystal cave sparkled like diamonds.',
        synonyms=['gem', 'jewel', 'stone'],
        phonetic='/ˈkristl/'
    ),
    'guardian': VocabularyWord(
        word='guardian',
        definition='Someone who protects and watches over something',
        difficulty='medium',
        category='characters',
        example='The guardian of the temple asked three questions.',
        synonyms=['protector', 'keeper', 'defender'],
        phonetic='/ˈɡärdēən/'
    ),
    'portal': VocabularyWord(
        word='portal',
        definition='A magical doorway or entrance to another place',
        difficulty='medium',
        category='magic',
        example='The glowing portal led to a different world.',
        synonyms=['gateway', 'doorway', 'entrance'],
        phonetic='/ˈpôrtl/'
    ),
    'illuminate': VocabularyWord(
        word='illuminate',
        definition='To light up or make bright with light',
        difficulty='hard',
        category='action',
        example='The torch will illuminate the dark passage.',
        synonyms=['brighten', 'light up', 'glow'],
        phonetic='/əˈlo͞oməˌnāt/'
    ),
    'expedition': VocabularyWord(
        word='expedition',
        definition='A journey organized for a specific purpose',
        difficulty='hard',
        category='general',
        example='The expedition to find the lost city began at dawn.',
        synonyms=['journey', 'adventure', 'quest'],
        phonetic='/ˌekspəˈdiSH(ə)n/'
    ),
    'magnificent': VocabularyWord(
        word='magnificent',
        definition='Very beautiful, impressive, or wonderful',
        difficulty='medium',
        category='descriptive',
        example='The magnificent palace had golden towers.',
        synonyms=['splendid', 'wonderful', 'amazing'],
        phonetic='/maɡˈnifəsənt/'
    ),
    'perseverance': VocabularyWord(
        word='perseverance',
        definition='Continuing to try hard even when things are difficult',
        difficulty='hard',
        category='abstract',
        example='With perseverance, she solved the difficult puzzle.',
        synonyms=['determination', 'persistence', 'dedication'],
        phonetic='/ˌpərsəˈvirəns/'
    ),
    'sanctuary': VocabularyWord(
        word='sanctuary',
        definition='A safe place where someone or something is protected',
        difficulty='medium',
        category='places',
        example='The forest sanctuary protected all the animals.',
        synonyms=['refuge', 'shelter', 'haven'],
        phonetic='/ˈsaNG(k)CHo͞oˌerē/'
    ),
    'transform': VocabularyWord(
        word='transform',
        definition='To change completely in appearance or form',
        difficulty='medium',
        category='action',
        example='The magic spell will transform the pumpkin into a carriage.',
        synonyms=['change', 'convert', 'alter'],
        phonetic='/transˈfôrm/'
    ),
    'chronicle': VocabularyWord(
        word='chronicle',
        definition='A record or story of events in the order they happened',
        difficulty='hard',
        category='general',
        example='The ancient chronicle told of brave heroes.',
        synonyms=['record', 'history', 'story'],
        phonetic='/ˈkrän(ə)kəl/'
    )
}

def get_vocabulary_by_difficulty(difficulty: str) -> Dict[str, VocabularyWord]:
    """Get vocabulary words filtered by difficulty level"""
    return {
        word: data for word, data in VOCABULARY_DATABASE.items() 
        if data.difficulty == difficulty
    }

def get_vocabulary_by_category(category: str) -> Dict[str, VocabularyWord]:
    """Get vocabulary words filtered by category"""
    return {
        word: data for word, data in VOCABULARY_DATABASE.items() 
        if data.category == category
    }

def extract_vocabulary_from_text(text: str) -> list[str]:
    """Extract vocabulary words that appear in the given text"""
    import re
    words = re.findall(r'\b\w+\b', text.lower())
    return [word for word in words if word in VOCABULARY_DATABASE]
