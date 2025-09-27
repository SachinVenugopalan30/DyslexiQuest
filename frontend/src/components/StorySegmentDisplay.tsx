import { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

interface VisualCue {
  icon: string;
  description: string;
  position: 'before' | 'after' | 'inline';
}

interface MultipleChoice {
  id: string;
  text: string;
  is_correct: boolean;
  feedback: string;
  visual_cue?: VisualCue;
  difficulty_adjustment: number;
}

interface WordChallenge {
  type: 'completion' | 'matching' | 'spelling' | 'rhyme';
  instruction: string;
  word: string;
  options?: string[];
  correct_answer: string;
  hint: string;
  visual_cue?: VisualCue;
  difficulty_level: number;
}

interface StorySegment {
  id: string;
  text: string;
  visual_cues: VisualCue[];
  multiple_choices: MultipleChoice[];
  word_challenge?: WordChallenge;
  vocabulary_words: string[];
  difficulty_level: number;
  estimated_reading_time: number;
}

interface StorySegmentProps {
  segment: StorySegment;
  onChoice: (choiceId: string) => void;
  onChallenge?: (response: string) => void;
  isLoading?: boolean;
  textToSpeechEnabled?: boolean;
  showChallenge?: boolean;
}

export const StorySegmentDisplay: React.FC<StorySegmentProps> = ({
  segment,
  onChoice,
  onChallenge,
  isLoading = false,
  textToSpeechEnabled = false,
  showChallenge = false
}) => {
  const [selectedChoice, setSelectedChoice] = useState<string>('');
  const [challengeResponse, setChallengeResponse] = useState<string>('');
  const [isReading, setIsReading] = useState(false);

  const speakText = (text: string) => {
    if (textToSpeechEnabled && 'speechSynthesis' in window) {
      setIsReading(true);
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8; // Slower for dyslexic children
      utterance.pitch = 1.1; // Slightly higher pitch
      utterance.volume = 0.8;
      
      utterance.onend = () => setIsReading(false);
      utterance.onerror = () => setIsReading(false);
      
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsReading(false);
    }
  };

  const handleChoice = (choiceId: string) => {
    setSelectedChoice(choiceId);
    onChoice(choiceId);
  };

  const handleChallengeSubmit = () => {
    if (challengeResponse.trim() && onChallenge) {
      onChallenge(challengeResponse.trim());
    }
  };

  const renderTextWithVisualCues = (text: string, visualCues: VisualCue[]) => {
    let renderedText = text;
    
    // Add emojis that are already in the text or insert visual cues
    visualCues.forEach(cue => {
      if (!renderedText.includes(cue.icon)) {
        // Insert icon based on position
        if (cue.position === 'before') {
          renderedText = `${cue.icon} ${renderedText}`;
        } else if (cue.position === 'after') {
          renderedText = `${renderedText} ${cue.icon}`;
        }
      }
    });

    return renderedText;
  };

  return (
    <div className="story-segment bg-retro-black border-2 border-retro-green rounded-lg p-6 mb-6">
      {/* Text-to-Speech Controls */}
      {textToSpeechEnabled && (
        <div className="flex justify-end mb-4">
          <button
            onClick={isReading ? stopSpeaking : () => speakText(segment.text)}
            className="btn-secondary text-sm px-3 py-2 flex items-center space-x-2"
            aria-label={isReading ? "Stop reading" : "Read text aloud"}
          >
            {isReading ? <VolumeX size={16} /> : <Volume2 size={16} />}
            <span>{isReading ? "Stop" : "Read Aloud"}</span>
          </button>
        </div>
      )}

      {/* Story Text with Visual Cues */}
      <div className="story-text mb-6">
        <p 
          className="text-lg leading-relaxed dyslexia-friendly text-retro-green"
          style={{ 
            fontSize: '1.25rem',
            lineHeight: '1.8',
            letterSpacing: '0.05em',
            wordSpacing: '0.16em'
          }}
        >
          {renderTextWithVisualCues(segment.text, segment.visual_cues)}
        </p>
      </div>

      {/* Word Challenge Section */}
      {showChallenge && segment.word_challenge && (
        <div className="word-challenge bg-retro-dark-green bg-opacity-20 border border-retro-amber rounded-lg p-4 mb-6">
          <h3 className="text-retro-amber font-bold mb-3 flex items-center">
            {segment.word_challenge.visual_cue?.icon} Word Challenge!
          </h3>
          
          <p className="text-retro-green mb-4 dyslexia-friendly">
            {segment.word_challenge.instruction}
          </p>

          {segment.word_challenge.type === 'matching' && segment.word_challenge.options ? (
            <div className="grid grid-cols-2 gap-3">
              {segment.word_challenge.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => setChallengeResponse(option)}
                  className={`p-3 border-2 rounded-lg font-medium transition-all duration-200 ${
                    challengeResponse === option
                      ? 'border-retro-amber bg-retro-amber bg-opacity-20 text-retro-amber'
                      : 'border-retro-green text-retro-green hover:border-retro-amber hover:text-retro-amber'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex space-x-3">
              <input
                type="text"
                value={challengeResponse}
                onChange={(e) => setChallengeResponse(e.target.value)}
                className="flex-1 p-3 bg-retro-black border-2 border-retro-green rounded-lg text-retro-green dyslexia-friendly text-lg"
                placeholder="Type your answer..."
                style={{ letterSpacing: '0.05em' }}
              />
            </div>
          )}

          <button
            onClick={handleChallengeSubmit}
            disabled={!challengeResponse.trim() || isLoading}
            className="btn-primary mt-3 px-4 py-2 disabled:opacity-50"
          >
            Submit Answer
          </button>
        </div>
      )}

      {/* Multiple Choice Options */}
      {!showChallenge && (
        <div className="multiple-choices">
          <h3 className="text-retro-amber font-bold mb-4 text-lg">
            What would you like to do?
          </h3>
          
          <div className="space-y-3">
            {segment.multiple_choices.map((choice) => (
              <button
                key={choice.id}
                onClick={() => handleChoice(choice.id)}
                disabled={isLoading}
                className={`w-full p-4 text-left border-2 rounded-lg font-medium transition-all duration-200 dyslexia-friendly ${
                  selectedChoice === choice.id
                    ? 'border-retro-amber bg-retro-amber bg-opacity-20 text-retro-amber'
                    : 'border-retro-green text-retro-green hover:border-retro-amber hover:bg-retro-amber hover:bg-opacity-10 hover:text-retro-amber'
                } disabled:opacity-50`}
                style={{ 
                  fontSize: '1.1rem',
                  lineHeight: '1.6',
                  letterSpacing: '0.05em'
                }}
              >
                <div className="flex items-center space-x-3">
                  {choice.visual_cue && (
                    <span className="text-2xl" role="img" aria-label={choice.visual_cue.description}>
                      {choice.visual_cue.icon}
                    </span>
                  )}
                  <span>{choice.text}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center mt-4">
          <div className="loading-spinner w-6 h-6 mx-auto mb-2"></div>
          <p className="text-retro-green text-sm">Thinking...</p>
        </div>
      )}
    </div>
  );
};
