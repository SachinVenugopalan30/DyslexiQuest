import { useState, useEffect, useRef } from 'react';

interface DecryptedTextProps {
  text: string;
  className?: string;
  startAnimation?: boolean;
  animationDuration?: number;
  scrambleChars?: string;
}

export const DecryptedText: React.FC<DecryptedTextProps> = ({
  text,
  className = '',
  startAnimation = true,
  animationDuration = 2000,
  scrambleChars = '█▓▒░/\\|_-=+*^%$#@!<>{}[]()~`',
}) => {
  const [displayText, setDisplayText] = useState('');
  const [isAnimating, setIsAnimating] = useState(false);
  const intervalRef = useRef<number | null>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    if (!startAnimation) {
      setDisplayText(text);
      return;
    }

    setIsAnimating(true);
    setDisplayText('');

    // Start the decryption animation
    const startTime = Date.now();
    const textLength = text.length;
    
    // Function to get a random scramble character
    const getRandomChar = () => scrambleChars[Math.floor(Math.random() * scrambleChars.length)];
    
    // Function to generate scrambled text for positions not yet revealed
    const generateScrambledText = (revealedLength: number) => {
      let result = '';
      for (let i = 0; i < textLength; i++) {
        if (i < revealedLength) {
          result += text[i];
        } else {
          // Keep original character if it's whitespace or special formatting
          if (text[i] === ' ' || text[i] === '\n' || text[i] === '\t') {
            result += text[i];
          } else {
            result += getRandomChar();
          }
        }
      }
      return result;
    };

    const animateDecryption = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / animationDuration, 1);
      
      // Calculate how many characters should be revealed
      const revealedLength = Math.floor(progress * textLength);
      
      // Generate the display text with some randomness in the scrambled portion
      const scrambledText = generateScrambledText(revealedLength);
      setDisplayText(scrambledText);
      
      if (progress < 1) {
        animationRef.current = setTimeout(animateDecryption, 50); // Update every 50ms for smooth effect
      } else {
        // Animation complete
        setDisplayText(text);
        setIsAnimating(false);
      }
    };

    // Start animation after a small delay
    animationRef.current = setTimeout(animateDecryption, 100);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (animationRef.current) clearTimeout(animationRef.current);
    };
  }, [text, startAnimation, animationDuration, scrambleChars]);

  return (
    <span className={`${className} ${isAnimating ? 'animate-pulse' : ''}`}>
      {displayText}
    </span>
  );
};
