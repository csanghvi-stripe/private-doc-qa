import { useEffect, useRef, useState } from 'react';
import { Bot, User, AlertTriangle, FileText, ChevronDown, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import type { Message, Source } from '../App';

interface ChatAreaProps {
  messages: Message[];
  isProcessing: boolean;
}

export default function ChatArea({ messages, isProcessing }: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.length === 0 && !isProcessing && (
        <EmptyState />
      )}

      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isProcessing && (
        <div className="flex items-start gap-4 message-enter">
          <div className="w-9 h-9 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          </div>
          <div className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-sm px-5 py-4">
            <div className="flex gap-1.5">
              <span className="w-2 h-2 bg-gray-400 rounded-full loading-dot" />
              <span className="w-2 h-2 bg-gray-400 rounded-full loading-dot" />
              <span className="w-2 h-2 bg-gray-400 rounded-full loading-dot" />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-8">
      <div className="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center mb-4">
        <Bot className="w-8 h-8 text-primary-600 dark:text-primary-400" />
      </div>
      <h2 className="text-lg font-semibold text-gray-700 dark:text-gray-200 mb-2">
        Ask about your documents
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md">
        Add some documents to the left, then ask questions about them.
        Everything is processed locally on your device.
      </p>
      <div className="mt-6 space-y-2 text-left">
        <p className="text-xs text-gray-400 dark:text-gray-500">Try asking:</p>
        <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
          <li>• "What's my total income for 2024?"</li>
          <li>• "When does my lease expire?"</li>
          <li>• "What medications am I allergic to?"</li>
        </ul>
      </div>
    </div>
  );
}

interface MessageBubbleProps {
  message: Message;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';
  const [sourcesExpanded, setSourcesExpanded] = useState(false);

  return (
    <div className={`flex items-start gap-4 message-enter ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`
        w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0
        ${isUser
          ? 'bg-gray-200 dark:bg-gray-700'
          : isSystem
            ? 'bg-yellow-100 dark:bg-yellow-900'
            : 'bg-primary-100 dark:bg-primary-900'
        }
      `}>
        {isUser ? (
          <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        ) : isSystem ? (
          <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
        ) : (
          <Bot className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        )}
      </div>

      {/* Message Content */}
      <div className={`
        flex-1 max-w-[85%] rounded-2xl px-5 py-4
        ${isUser
          ? 'bg-primary-600 text-white rounded-tr-sm'
          : isSystem
            ? 'bg-yellow-50 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 rounded-tl-sm'
            : 'bg-gray-100 dark:bg-gray-800 rounded-tl-sm'
        }
      `}>
        {/* Message text with markdown rendering for assistant messages */}
        {isUser ? (
          <p className="text-sm text-white selectable">{message.content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none selectable prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5 prose-headings:my-3 prose-headings:font-semibold">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Sources - Collapsible */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setSourcesExpanded(!sourcesExpanded)}
              className="flex items-center gap-2 text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              {sourcesExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
              <FileText className="w-3.5 h-3.5" />
              <span>
                {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
                ({Math.round((message.confidence || 0) * 100)}% confidence)
              </span>
            </button>

            {sourcesExpanded && (
              <div className="mt-3 space-y-2">
                {message.sources.map((source, idx) => (
                  <SourceItem key={idx} source={source} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className={`
          text-xs mt-3
          ${isUser ? 'text-primary-200' : 'text-gray-400 dark:text-gray-500'}
        `}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}

function SourceItem({ source }: { source: Source }) {
  return (
    <div className="p-3 bg-white/50 dark:bg-gray-900/50 rounded-lg text-xs border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 mb-1.5">
        <FileText className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
        <span className="font-medium text-gray-700 dark:text-gray-200 truncate">
          {source.document}
        </span>
        {source.page && (
          <span className="text-gray-400 text-[10px]">p.{source.page}</span>
        )}
        <span className="ml-auto text-primary-600 dark:text-primary-400 font-medium">
          {Math.round(source.score * 100)}%
        </span>
      </div>
      <p className="text-gray-500 dark:text-gray-400 line-clamp-2 selectable leading-relaxed">
        {source.snippet}
      </p>
    </div>
  );
}
