import { FileText, Trash2, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import type { Document } from '../App';

interface DocumentListProps {
  documents: Document[];
  onRemove: (name: string) => void;
  isIndexing: boolean;
}

export default function DocumentList({ documents, onRemove, isIndexing }: DocumentListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Documents
        </h2>
        <span className="text-xs text-gray-400 dark:text-gray-500">
          {documents.filter(d => d.status === 'indexed').length} indexed
        </span>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-3" />
          <p className="text-sm text-gray-500 dark:text-gray-400">
            No documents yet
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            Drag & drop files below
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          {documents.map((doc) => (
            <DocumentItem
              key={doc.name}
              document={doc}
              onRemove={() => onRemove(doc.name)}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

interface DocumentItemProps {
  document: Document;
  onRemove: () => void;
}

function DocumentItem({ document, onRemove }: DocumentItemProps) {
  const statusIcon = {
    pending: <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />,
    indexing: <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />,
    indexed: <CheckCircle className="w-4 h-4 text-green-500" />,
    error: <AlertCircle className="w-4 h-4 text-red-500" />,
  }[document.status];

  return (
    <li className="group flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
      <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
      
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-700 dark:text-gray-200 truncate">
          {document.name}
        </p>
        {document.status === 'indexed' && (
          <p className="text-xs text-gray-400 dark:text-gray-500">
            {document.chunks} chunks
          </p>
        )}
        {document.error && (
          <p className="text-xs text-red-500 truncate">
            {document.error}
          </p>
        )}
      </div>

      <div className="flex items-center gap-1">
        {statusIcon}
        <button
          onClick={onRemove}
          className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
          title="Remove document"
        >
          <Trash2 className="w-3.5 h-3.5 text-gray-400 hover:text-red-500" />
        </button>
      </div>
    </li>
  );
}
