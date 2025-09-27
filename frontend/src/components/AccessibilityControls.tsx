import { useState } from 'react';
import { Settings, Volume2, VolumeX, Eye, EyeOff, Type, Palette } from 'lucide-react';
import { GameSettings } from '../App';

interface AccessibilityControlsProps {
  settings: GameSettings;
  onSettingChange: <K extends keyof GameSettings>(key: K, value: GameSettings[K]) => void;
  inline?: boolean;
}

export const AccessibilityControls: React.FC<AccessibilityControlsProps> = ({
  settings,
  onSettingChange,
  inline = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={inline ? "relative" : "fixed top-6 right-6 z-50"}>
      {/* Settings Toggle Button */}
      <button
        onClick={togglePanel}
        className={`${inline ? 'p-2' : 'p-3'} bg-retro-black border-2 border-retro-green text-retro-green hover:bg-retro-green hover:text-retro-black focus:outline-none focus:ring-2 focus:ring-retro-green transition-all duration-200 rounded ${!inline ? 'shadow-lg' : ''}`}
        aria-label={isOpen ? 'Close accessibility settings' : 'Open accessibility settings'}
        aria-expanded={isOpen}
        aria-controls="accessibility-panel"
      >
        <Settings size={inline ? 18 : 20} />
      </button>

      {/* Settings Panel */}
      {isOpen && (
        <div
          id="accessibility-panel"
          className={`absolute ${inline ? 'top-12 right-0 max-w-sm' : 'top-12 right-0 w-80'} ${inline ? 'w-72' : 'w-80'} bg-retro-black border-2 border-retro-green p-4 rounded shadow-lg z-50`}
          role="region"
          aria-labelledby="accessibility-title"
        >
          <h2 
            id="accessibility-title"
            className="text-retro-amber font-bold mb-4 text-lg"
          >
            ACCESSIBILITY SETTINGS
          </h2>

          {/* Font Size Control */}
          <div className="mb-4">
            <label className="block text-retro-green text-sm font-medium mb-2">
              <Type className="inline w-4 h-4 mr-2" />
              Text Size
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['small', 'medium', 'large'] as const).map((size) => (
                <button
                  key={size}
                  onClick={() => onSettingChange('fontSize', size)}
                  className={`px-3 py-2 border border-retro-green text-sm font-medium transition-all duration-200 ${
                    settings.fontSize === size
                      ? 'bg-retro-green text-retro-black'
                      : 'text-retro-green hover:bg-retro-green hover:text-retro-black'
                  }`}
                  aria-pressed={settings.fontSize === size}
                >
                  {size.charAt(0).toUpperCase() + size.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Theme Control */}
          <div className="mb-4">
            <label className="block text-retro-green text-sm font-medium mb-2">
              <Palette className="inline w-4 h-4 mr-2" />
              Display Theme
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => onSettingChange('theme', 'retro')}
                className={`px-3 py-2 border border-retro-green text-sm font-medium transition-all duration-200 ${
                  settings.theme === 'retro'
                    ? 'bg-retro-green text-retro-black'
                    : 'text-retro-green hover:bg-retro-green hover:text-retro-black'
                }`}
                aria-pressed={settings.theme === 'retro'}
              >
                Retro MS-DOS
              </button>
              <button
                onClick={() => onSettingChange('theme', 'accessible')}
                className={`px-3 py-2 border border-retro-green text-sm font-medium transition-all duration-200 ${
                  settings.theme === 'accessible'
                    ? 'bg-retro-green text-retro-black'
                    : 'text-retro-green hover:bg-retro-green hover:text-retro-black'
                }`}
                aria-pressed={settings.theme === 'accessible'}
              >
                High Contrast
              </button>
            </div>
          </div>

          {/* Font Family Control */}
          <div className="mb-4">
            <label className="block text-retro-green text-sm font-medium mb-2">
              Font Style
            </label>
            <div className="space-y-2">
              {[
                { value: 'mono', label: 'Monospace (Traditional)' },
                { value: 'dyslexic', label: 'OpenDyslexic (Dyslexia-Friendly)' },
                { value: 'accessible', label: 'Atkinson Hyperlegible (Clear)' },
              ].map(({ value, label }) => (
                <button
                  key={value}
                  onClick={() => onSettingChange('fontFamily', value as GameSettings['fontFamily'])}
                  className={`w-full text-left px-3 py-2 border border-retro-green text-sm font-medium transition-all duration-200 ${
                    settings.fontFamily === value
                      ? 'bg-retro-green text-retro-black'
                      : 'text-retro-green hover:bg-retro-green hover:text-retro-black'
                  }`}
                  aria-pressed={settings.fontFamily === value}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Animation Control */}
          <div className="mb-4">
            <label className="block text-retro-green text-sm font-medium mb-2">
              <Volume2 className="inline w-4 h-4 mr-2" />
              Animations
            </label>
            <button
              onClick={() => onSettingChange('skipAnimations', !settings.skipAnimations)}
              className={`w-full px-3 py-2 border border-retro-green text-sm font-medium transition-all duration-200 flex items-center justify-between ${
                !settings.skipAnimations
                  ? 'bg-retro-green text-retro-black'
                  : 'text-retro-green hover:bg-retro-green hover:text-retro-black'
              }`}
              aria-pressed={!settings.skipAnimations}
            >
              <span>Typing Animation</span>
              {settings.skipAnimations ? (
                <VolumeX className="w-4 h-4" />
              ) : (
                <Volume2 className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Keyboard Shortcuts Info */}
          <div className="border-t border-retro-green pt-4">
            <h3 className="text-retro-amber text-sm font-medium mb-2">
              Keyboard Shortcuts
            </h3>
            <div className="text-xs text-retro-green space-y-1">
              <div><kbd className="bg-retro-green text-retro-black px-1 rounded">Tab</kbd> Navigate elements</div>
              <div><kbd className="bg-retro-green text-retro-black px-1 rounded">Enter</kbd> Activate buttons</div>
              <div><kbd className="bg-retro-green text-retro-black px-1 rounded">Esc</kbd> Close panels</div>
              <div><kbd className="bg-retro-green text-retro-black px-1 rounded">↑↓</kbd> Navigate options</div>
            </div>
          </div>

          {/* Close Button */}
          <button
            onClick={togglePanel}
            className="w-full mt-4 px-3 py-2 border border-retro-amber text-retro-amber hover:bg-retro-amber hover:text-retro-black focus:outline-none focus:ring-2 focus:ring-retro-amber transition-all duration-200 text-sm"
            aria-label="Close accessibility settings"
          >
            CLOSE
          </button>
        </div>
      )}

      {/* Screen reader instructions */}
      <div className="sr-only" aria-live="polite">
        {isOpen && 'Accessibility settings panel opened. Use Tab to navigate through options.'}
      </div>
    </div>
  );
};
