import { Shield, AlertCircle, X, Wifi, WifiOff } from 'lucide-react';

interface StatusBarProps {
  backendReady: boolean;
  documentCount: number;
  chunkCount: number;
  error: string | null;
  onClearError: () => void;
}

export default function StatusBar({
  backendReady,
  documentCount,
  chunkCount,
  error,
  onClearError,
}: StatusBarProps) {
  return (
    <footer className="h-7 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 flex items-center justify-between text-xs">
      {/* Left side - Privacy indicator */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-green-600 dark:text-green-400">
          <Shield className="w-3.5 h-3.5" />
          <span>100% on-device</span>
        </div>

        <div className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
          {backendReady ? (
            <>
              <Wifi className="w-3.5 h-3.5 text-green-500" />
              <span>Backend ready</span>
            </>
          ) : (
            <>
              <WifiOff className="w-3.5 h-3.5 text-yellow-500" />
              <span>Connecting...</span>
            </>
          )}
        </div>
      </div>

      {/* Center - Error message */}
      {error && (
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 px-3 py-1 rounded-full">
          <AlertCircle className="w-3.5 h-3.5" />
          <span className="truncate max-w-xs">{error}</span>
          <button
            onClick={onClearError}
            className="p-0.5 hover:bg-red-100 dark:hover:bg-red-900/40 rounded"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Right side - Document stats */}
      <div className="flex items-center gap-4 text-gray-500 dark:text-gray-400">
        <span>{documentCount} documents</span>
        <span>{chunkCount.toLocaleString()} chunks</span>
      </div>
    </footer>
  );
}
