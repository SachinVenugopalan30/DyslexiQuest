import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { GameSettings } from '../App';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: GameSettings;
  onSettingChange: <K extends keyof GameSettings>(key: K, value: GameSettings[K]) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  onSettingChange
}) => {
  // Add/remove body class for modal state
  useEffect(() => {
    if (isOpen) {
      document.body.classList.add('modal-open');
      document.body.style.overflow = 'hidden';
    } else {
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
    }

    return () => {
      document.body.classList.remove('modal-open');
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Cleanup modal container on unmount
  useEffect(() => {
    return () => {
      const container = document.getElementById('settings-modal-container');
      if (container && !document.querySelector('[data-settings-modal-active]')) {
        container.remove();
      }
    };
  }, []);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Create or get a container at the end of the body for the modal
  let modalContainer = document.getElementById('settings-modal-container');
  if (!modalContainer) {
    modalContainer = document.createElement('div');
    modalContainer.id = 'settings-modal-container';
    modalContainer.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999;';
  }
  
  // Always ensure the modal container is the last element in the body
  if (modalContainer.parentNode !== document.body || modalContainer !== document.body.lastElementChild) {
    document.body.appendChild(modalContainer);
  }

  const modalContent = (
    <div 
      className="portal-settings-modal"
      onClick={onClose}
      style={{ pointerEvents: 'auto' }}
      data-settings-modal-active="true"
    >
      <div 
        className={`
          portal-settings-modal-content rounded-lg p-8 shadow-2xl
          ${settings.highContrast 
            ? 'bg-black text-white border-2 border-white' 
            : 'bg-retro-black text-retro-lavender border-2 border-retro-green'
          }
        `}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-retro-amber">⚙️ Accessibility Settings</h3>
          <button
            onClick={onClose}
            className={`
              text-3xl font-bold transition-colors
              ${settings.highContrast 
                ? 'text-white hover:text-gray-300' 
                : 'text-retro-green hover:text-retro-amber'
              }
            `}
            aria-label="Close settings"
          >
            ✕
          </button>
        </div>
        
        {/* Font Size Setting */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold mb-3 text-retro-amber">📏 Font Size</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {(['small', 'medium', 'large', 'x-large'] as const).map((size) => (
              <button
                key={size}
                onClick={() => onSettingChange('fontSize', size)}
                className={`
                  p-2 rounded border transition-all
                  ${settings.fontSize === size 
                    ? settings.highContrast
                      ? 'bg-white text-black border-white'
                      : 'bg-retro-green text-retro-black border-retro-green'
                    : settings.highContrast
                      ? 'bg-black text-white border-white hover:bg-gray-800'
                      : 'bg-retro-black text-retro-lavender border-retro-green hover:bg-retro-green hover:text-retro-black'
                  }
                `}
              >
                {size === 'x-large' ? 'X-Large' : size.charAt(0).toUpperCase() + size.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Font Family Setting */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold mb-3 text-retro-amber">🔤 Font Style</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <button
              onClick={() => onSettingChange('fontFamily', 'opendyslexic')}
              className={`
                p-3 rounded border transition-all text-left
                ${settings.fontFamily === 'opendyslexic' 
                  ? settings.highContrast
                    ? 'bg-white text-black border-white'
                    : 'bg-retro-green text-retro-black border-retro-green'
                  : settings.highContrast
                    ? 'bg-black text-white border-white hover:bg-gray-800'
                    : 'bg-retro-black text-retro-lavender border-retro-green hover:bg-retro-green hover:text-retro-black'
                }
              `}
            >
              <div className="font-dyslexic">OpenDyslexic</div>
              <div className="text-sm opacity-75">Dyslexia-friendly font</div>
            </button>
            <button
              onClick={() => onSettingChange('fontFamily', 'poppins')}
              className={`
                p-3 rounded border transition-all text-left
                ${settings.fontFamily === 'poppins' 
                  ? settings.highContrast
                    ? 'bg-white text-black border-white'
                    : 'bg-retro-green text-retro-black border-retro-green'
                  : settings.highContrast
                    ? 'bg-black text-white border-white hover:bg-gray-800'
                    : 'bg-retro-black text-retro-lavender border-retro-green hover:bg-retro-green hover:text-retro-black'
                }
              `}
            >
              <div className="font-poppins">Poppins</div>
              <div className="text-sm opacity-75">Standard readable font</div>
            </button>
          </div>
        </div>

        {/* High Contrast Setting */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold mb-3 text-retro-amber">🔲 High Contrast Mode</h4>
          <button
            onClick={() => onSettingChange('highContrast', !settings.highContrast)}
            className={`
              w-full p-3 rounded border transition-all text-left
              ${settings.highContrast 
                ? 'bg-white text-black border-white'
                : 'bg-retro-black text-retro-lavender border-retro-green hover:bg-retro-green hover:text-retro-black'
              }
            `}
          >
            <div className="flex items-center justify-between">
              <span>{settings.highContrast ? '✅ High Contrast ON' : '⬜ High Contrast OFF'}</span>
              <span className="text-sm">
                {settings.highContrast ? 'Black & White theme' : 'Click to enable'}
              </span>
            </div>
          </button>
        </div>

        <div className="text-center">
          <button
            onClick={onClose}
            className={`
              px-6 py-2 rounded font-semibold transition-all
              ${settings.highContrast 
                ? 'bg-white text-black hover:bg-gray-200'
                : 'bg-retro-amber text-retro-black hover:bg-retro-green'
              }
            `}
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );

  // Render modal as a portal to the dedicated container
  return createPortal(modalContent, modalContainer);
};
