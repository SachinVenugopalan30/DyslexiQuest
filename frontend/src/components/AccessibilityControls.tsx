import { useState } from 'react';
import { Settings } from 'lucide-react';
import { GameSettings } from '../App';
import { SettingsModal } from './SettingsModal';

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
  const [isModalOpen, setIsModalOpen] = useState(false);
  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <div className={inline ? "relative" : "fixed top-6 right-6 z-50"}>
      {/* Settings Toggle Button */}
      <button
        onClick={openModal}
        className={`${inline ? 'p-2' : 'p-3'} bg-primary-gunmetal border-2 border-primary-green text-primary-lavender hover:bg-primary-green hover:text-primary-gunmetal focus:outline-none focus:ring-2 focus:ring-primary-powder transition-all duration-200 rounded ${!inline ? 'shadow-lg' : ''}`}
        aria-label={isModalOpen ? 'Close accessibility settings' : 'Open accessibility settings'}
        aria-expanded={isModalOpen}
        aria-controls="settings-modal"
      >
        <Settings size={inline ? 18 : 20} />
      </button>

      {/* Portal-based Settings Modal */}
      <SettingsModal
        isOpen={isModalOpen}
        onClose={closeModal}
        settings={settings}
        onSettingChange={onSettingChange}
      />
    </div>
  );
};
