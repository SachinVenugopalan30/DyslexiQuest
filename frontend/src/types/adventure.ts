// Adventure theme system types

export interface AdventureTheme {
  id: 'forest' | 'space' | 'magical' | 'mystery';
  name: string;
  displayName: string;
  description: string;
  characterImage: string;
  backgroundImage: string;
  primaryColor: string;
  secondaryColor: string;
  icon: string;
}

export interface AdventureConfig {
  themes: Record<AdventureTheme['id'], AdventureTheme>;
}

// Adventure theme configurations
export const ADVENTURE_THEMES: AdventureConfig = {
  themes: {
    forest: {
      id: 'forest',
      name: 'FOREST FRIENDS',
      displayName: 'Forest Adventure',
      description: 'Explore the magical forest and meet friendly creatures',
      characterImage: './src/assets/forest_friend.png',
      backgroundImage: './src/assets/forest_friend_background.png',
      primaryColor: '#228B22',
      secondaryColor: '#90EE90',
      icon: '🌲'
    },
    space: {
      id: 'space',
      name: 'GALAXY QUEST',
      displayName: 'Space Adventure',
      description: 'Journey through space and discover new worlds',
      characterImage: './src/assets/galaxy_quest.png',
      backgroundImage: './src/assets/galaxy_quest_background.png',
      primaryColor: '#4169E1',
      secondaryColor: '#87CEEB',
      icon: '🚀'
    },
    magical: {
      id: 'magical',
      name: 'MAGICAL CASTLE',
      displayName: 'Magical Dungeon',
      description: 'Enter the enchanted castle and solve magical mysteries',
      characterImage: './src/assets/magical_castle.png',
      backgroundImage: './src/assets/magical_castle_background.png',
      primaryColor: '#9932CC',
      secondaryColor: '#DDA0DD',
      icon: '✨'
    },
    mystery: {
      id: 'mystery',
      name: 'SECRET ISLAND',
      displayName: 'Secret Island Adventure',
      description: 'Uncover secrets on a mysterious tropical island',
      characterImage: './src/assets/secret_island.png',
      backgroundImage: './src/assets/secret_island_background.png',
      primaryColor: '#20B2AA',
      secondaryColor: '#AFEEEE',
      icon: '🏝️'
    }
  }
};

// Helper functions
export const getAdventureTheme = (id: AdventureTheme['id']): AdventureTheme => {
  return ADVENTURE_THEMES.themes[id];
};

export const getAllAdventureThemes = (): AdventureTheme[] => {
  return Object.values(ADVENTURE_THEMES.themes);
};

// Map adventure types to backend genre parameters
export const genreMapping: Record<AdventureTheme['id'], 'forest' | 'space' | 'dungeon' | 'mystery'> = {
  forest: 'forest',
  space: 'space',
  magical: 'dungeon',
  mystery: 'mystery'
};
