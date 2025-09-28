import { AdventureTheme } from '../types/adventure';

interface ThemedLoadingScreenProps {
  selectedAdventure?: AdventureTheme | null;
}

export const ThemedLoadingScreen: React.FC<ThemedLoadingScreenProps> = ({ selectedAdventure }) => {
  // Default values for when no adventure is selected
  const adventure = selectedAdventure || {
    name: 'YOUR ADVENTURE',
    displayName: 'Adventure',
    icon: '🎭',
    primaryColor: '#5A7D7C',
    secondaryColor: '#A0C1D1'
  };

  // Generate theme-specific content
  const getThemeContent = () => {
    const adventureId = 'id' in adventure ? adventure.id : undefined;
    switch (adventureId) {
      case 'forest':
        return {
          title: '🌲 Creating Your Forest Adventure!',
          subtitle: 'Our AI is crafting a magical forest story just for you...',
          activities: [
            '🌿 Growing magical trees',
            '🦋 Gathering forest friends',
            '🍄 Preparing nature puzzles'
          ]
        };
      case 'space':
        return {
          title: '🚀 Creating Your Space Adventure!',
          subtitle: 'Our AI is launching an amazing cosmic journey just for you...',
          activities: [
            '⭐ Building star systems',
            '👽 Meeting friendly aliens',
            '🛸 Preparing space missions'
          ]
        };
      case 'magical':
        return {
          title: '✨ Creating Your Magical Adventure!',
          subtitle: 'Our AI is casting spells for an enchanted story just for you...',
          activities: [
            '🏰 Building magical castles',
            '🧙‍♂️ Gathering wise wizards',
            '💎 Hiding ancient treasures'
          ]
        };
      case 'mystery':
        return {
          title: '🏝️ Creating Your Island Adventure!',
          subtitle: 'Our AI is crafting a tropical paradise story just for you...',
          activities: [
            '🌴 Growing palm trees',
            '🗺️ Drawing treasure maps',
            '🏖️ Preparing beach adventures'
          ]
        };
      default:
        return {
          title: '🎭 Creating Your Adventure!',
          subtitle: 'Our AI storyteller is crafting a unique adventure just for you...',
          activities: [
            '✨ Generating story elements',
            '🎯 Setting up challenges', 
            '📚 Preparing vocabulary words'
          ]
        };
    }
  };

  const themeContent = getThemeContent();

  return (
    <div 
      className="min-h-screen flex items-center justify-center"
      style={{
        background: `linear-gradient(135deg, ${adventure.primaryColor}20, ${adventure.secondaryColor}20)`
      }}
    >
      <div className="text-center max-w-md mx-auto p-8">
        <div className="mb-8">
          {/* Themed loading spinner */}
          <div 
            className="loading-spinner w-16 h-16 mx-auto mb-6"
            style={{
              borderTopColor: adventure.primaryColor,
              borderRightColor: adventure.secondaryColor
            }}
          />
          
          {/* Themed title */}
          <h2 
            className="text-2xl font-bold mb-4"
            style={{ color: adventure.primaryColor }}
          >
            {themeContent.title}
          </h2>
          
          {/* Themed subtitle */}
          <p 
            className="leading-relaxed mb-4"
            style={{ color: adventure.primaryColor, opacity: 0.8 }}
          >
            {themeContent.subtitle}
          </p>
          
          {/* Themed activities */}
          <div 
            className="text-sm opacity-80"
            style={{ color: adventure.primaryColor }}
          >
            {themeContent.activities.map((activity, index) => (
              <p key={index} className="mb-1">{activity}</p>
            ))}
          </div>
        </div>
        
        {/* Themed animated dots */}
        <div className="flex justify-center space-x-2 mb-4">
          <div 
            className="w-2 h-2 rounded-full animate-pulse delay-0"
            style={{ backgroundColor: adventure.primaryColor }}
          />
          <div 
            className="w-2 h-2 rounded-full animate-pulse delay-200"
            style={{ backgroundColor: adventure.secondaryColor }}
          />
          <div 
            className="w-2 h-2 rounded-full animate-pulse delay-400"
            style={{ backgroundColor: adventure.primaryColor }}
          />
        </div>
        
        {/* Duration note */}
        <p 
          className="text-xs opacity-60"
          style={{ color: adventure.primaryColor }}
        >
          This usually takes 3-5 seconds
        </p>
      </div>
    </div>
  );
};
