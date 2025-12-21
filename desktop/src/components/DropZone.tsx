import { useCallback } from 'react';
import { open } from '@tauri-apps/plugin-dialog';
import { Plus, Upload } from 'lucide-react';

interface DropZoneProps {
  onFilesAdded: (paths: string[]) => void;
}

export default function DropZone({ onFilesAdded }: DropZoneProps) {
  const handleClick = useCallback(async () => {
    try {
      const selected = await open({
        multiple: true,
        filters: [{
          name: 'Documents',
          extensions: ['pdf', 'docx', 'doc', 'txt', 'md']
        }]
      });
      
      if (selected) {
        // selected is string or string[]
        const paths = Array.isArray(selected) ? selected : [selected];
        onFilesAdded(paths);
      }
    } catch (err) {
      console.error('File dialog error:', err);
    }
  }, [onFilesAdded]);

  return (
    <div className="p-4 border-t border-gray-200 dark:border-gray-700">
      <button
        onClick={handleClick}
        className="w-full border-2 border-dashed rounded-lg p-4 text-center cursor-pointer
          transition-all duration-200
          border-gray-300 dark:border-gray-600 
          hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800"
      >
        <Plus className="w-8 h-8 mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
          Add Documents
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          PDF, DOCX, TXT, MD
        </p>
      </button>
    </div>
  );
}