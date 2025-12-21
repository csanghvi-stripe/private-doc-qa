import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, Mic, MicOff, Loader2 } from 'lucide-react';

interface InputAreaProps {
  onSubmit: (question: string) => void;
  onVoiceInput: () => void;
  isProcessing: boolean;
  isRecording: boolean;
  disabled: boolean;
}

export default function InputArea({
  onSubmit,
  onVoiceInput,
  isProcessing,
  isRecording,
  disabled,
}: InputAreaProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !isProcessing && !disabled) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-900">
      <div className="flex items-end gap-2">
        {/* Text Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={disabled ? "Initializing..." : "Ask a question..."}
            disabled={disabled || isProcessing}
            rows={1}
            className={`
              w-full px-4 py-3 pr-12 rounded-xl resize-none
              bg-gray-100 dark:bg-gray-800
              text-gray-700 dark:text-gray-200
              placeholder-gray-400 dark:placeholder-gray-500
              border-2 border-transparent
              focus:border-primary-500 focus:outline-none focus:ring-0
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
            `}
          />
          
          {/* Send Button (inside textarea) */}
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isProcessing || disabled}
            className={`
              absolute right-2 bottom-2 p-2 rounded-lg
              transition-all duration-200
              ${input.trim() && !isProcessing && !disabled
                ? 'bg-primary-600 text-white hover:bg-primary-700'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
              }
            `}
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Voice Input Button */}
        <button
          onClick={onVoiceInput}
          disabled={isProcessing || disabled}
          className={`
            p-3 rounded-xl transition-all duration-200
            ${isRecording
              ? 'bg-red-500 text-white recording-indicator'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          title={isRecording ? "Recording..." : "Voice input"}
        >
          {isRecording ? (
            <MicOff className="w-5 h-5" />
          ) : (
            <Mic className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Recording indicator */}
      {isRecording && (
        <div className="mt-2 flex items-center gap-2 text-sm text-red-500">
          <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          Listening... Speak your question
        </div>
      )}

      {/* Keyboard hint */}
      <p className="mt-2 text-xs text-gray-400 dark:text-gray-500 text-center">
        Press <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs">Enter</kbd> to send, 
        <kbd className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs ml-1">Shift+Enter</kbd> for new line
      </p>
    </div>
  );
}
