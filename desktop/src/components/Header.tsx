import { Lock } from 'lucide-react';

export default function Header() {
  return (
    <header className="titlebar h-12 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center px-4">
      {/* macOS traffic lights spacing */}
      <div className="w-20" />
      
      {/* Title */}
      <div className="flex-1 flex items-center justify-center gap-2">
        <Lock className="w-4 h-4 text-primary-600 dark:text-primary-400" />
        <h1 className="text-sm font-semibold text-gray-700 dark:text-gray-200">
          Private Doc Q&A
        </h1>
      </div>
      
      {/* Spacer for symmetry */}
      <div className="w-20" />
    </header>
  );
}
