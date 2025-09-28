import { useState, useEffect } from 'react';
import { DecryptedText } from './DecryptedText';

interface AnimatedAsciiArtProps {
  className?: string;
  skipAnimations?: boolean;
}

export const AnimatedAsciiArt: React.FC<AnimatedAsciiArtProps> = ({ 
  className = '',
  skipAnimations = false 
}) => {
  const [startAnimation, setStartAnimation] = useState(false);

  // The ASCII art text
  const asciiText = `
██████╗  ██╗   ██╗ ███████╗ ██╗      ███████╗ ██╗  ██╗ ██╗  ██████╗  ██╗   ██╗ ███████╗ ███████╗ ████████╗
██╔══██╗ ╚██╗ ██╔╝ ██╔════╝ ██║      ██╔════╝ ╚██╗██╔╝ ██║ ██╔═══██╗ ██║   ██║ ██╔════╝ ██╔════╝ ╚══██╔══╝
██║  ██║  ╚████╔╝  ███████╗ ██║      █████╗    ╚███╔╝  ██║ ██║   ██║ ██║   ██║ █████╗   ███████╗    ██║   
██║  ██║   ╚██╔╝   ╚════██║ ██║      ██╔══╝    ██╔██╗  ██║ ██║▄▄ ██║ ██║   ██║ ██╔══╝   ╚════██║    ██║   
██████╔╝    ██║    ███████║ ███████╗ ███████╗ ██╔╝ ██╗ ██║ ╚██████╔╝ ╚██████╔╝ ███████╗ ███████║    ██║   
╚═════╝     ╚═╝    ╚══════╝ ╚══════╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝  ╚══▀▀═╝   ╚═════╝  ╚══════╝ ╚══════╝    ╚═╝   `;

  useEffect(() => {
    // Start animation after component mounts with a small delay
    const timer = setTimeout(() => {
      setStartAnimation(true);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  if (skipAnimations) {
    return (
      <pre 
        className={`text-retro-green text-xs sm:text-sm md:text-base whitespace-pre inline-block min-w-max ${className}`}
        aria-hidden="true"
      >
        {asciiText}
      </pre>
    );
  }

  return (
    <pre 
      className={`text-retro-green text-xs sm:text-sm md:text-base whitespace-pre inline-block min-w-max ${className}`}
      aria-hidden="true"
    >
      <DecryptedText
        text={asciiText}
        startAnimation={startAnimation}
        animationDuration={3000}
        scrambleChars="█▓▒░╔═║╗╚╝╬╦╩╠╣▀▄▌▐"
      />
    </pre>
  );
};
