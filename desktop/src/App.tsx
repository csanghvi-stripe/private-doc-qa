import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';

import Header from './components/Header';
import DocumentList from './components/DocumentList';
import ChatArea from './components/ChatArea';
import InputArea from './components/InputArea';
import StatusBar from './components/StatusBar';
import DropZone from './components/DropZone';

// Types
export interface Document {
  name: string;
  path: string;
  chunks: number;
  status: 'pending' | 'indexing' | 'indexed' | 'error';
  error?: string;
}

export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  sources?: Source[];
  confidence?: number;
  timestamp: Date;
}

export interface Source {
  document: string;
  page?: number;
  score: number;
  snippet: string;
}

export interface AppState {
  documents: Document[];
  messages: Message[];
  isIndexing: boolean;
  isProcessing: boolean;
  isRecording: boolean;
  error: string | null;
  backendReady: boolean;
}

function App() {
  const [state, setState] = useState<AppState>({
    documents: [],
    messages: [],
    isIndexing: false,
    isProcessing: false,
    isRecording: false,
    error: null,
    backendReady: false,
  });

  // Initialize backend connection
  useEffect(() => {
    const initBackend = async () => {
      try {
        const result = await invoke<{ ready: boolean; documents: Document[] }>('init_backend');
        setState(prev => ({
          ...prev,
          backendReady: result.ready,
          documents: result.documents || [],
        }));
      } catch (err) {
        console.error('Failed to initialize backend:', err);
        setState(prev => ({
          ...prev,
          error: 'Failed to connect to backend. Please restart the app.',
        }));
      }
    };

    initBackend();

    // Listen for backend events
    const unlistenProgress = listen<{ document: string; progress: number }>('indexing-progress', (event) => {
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc =>
          doc.name === event.payload.document
            ? { ...doc, status: 'indexing' as const }
            : doc
        ),
      }));
    });

    const unlistenComplete = listen<{ document: string; chunks: number }>('indexing-complete', (event) => {
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc =>
          doc.name === event.payload.document
            ? { ...doc, status: 'indexed' as const, chunks: event.payload.chunks }
            : doc
        ),
      }));
    });

    return () => {
      unlistenProgress.then(fn => fn());
      unlistenComplete.then(fn => fn());
    };
  }, []);

  // Handle file drop

// Handle file drop
  const handleFilesAdded = useCallback(async (paths: string[]) => {
    console.log('Adding files:', paths);
    
    const newDocs: Document[] = paths.map(p => ({
      name: p.split('/').pop() || p,
      path: p,
      chunks: 0,
      status: 'pending' as const,
    }));

    setState(prev => ({
      ...prev,
      documents: [...prev.documents, ...newDocs],
      isIndexing: true,
    }));

    try {
      const result = await invoke<Document[]>('add_documents', { paths });
      console.log('Add documents result:', result);
      
      // Update documents with result from backend
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => {
          const updated = result.find(r => r.name === doc.name);
          if (updated) {
            return { ...doc, ...updated, status: 'indexed' as const };
          }
          return doc;
        }),
        isIndexing: false,
      }));
    } catch (err) {
      console.error('Failed to add documents:', err);
      setState(prev => ({
        ...prev,
        documents: prev.documents.map(doc => 
          doc.status === 'pending' 
            ? { ...doc, status: 'error' as const, error: String(err) }
            : doc
        ),
        error: `Failed to add documents: ${err}`,
        isIndexing: false,
      }));
    }
  }, []);

  // Handle question submission
  const handleSubmitQuestion = useCallback(async (question: string) => {
    if (!question.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isProcessing: true,
    }));

    try {
      const response = await invoke<{
        answer: string;
        sources: Source[];
        confidence: number;
      }>('ask_question', { question });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isProcessing: false,
      }));
    } catch (err) {
      console.error('Failed to get answer:', err);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: `Error: ${err}`,
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isProcessing: false,
      }));
    }
  }, []);

  // Handle voice input
  const handleVoiceInput = useCallback(async () => {
    setState(prev => ({ ...prev, isRecording: true }));

    try {
      const transcription = await invoke<string>('record_and_transcribe');
      setState(prev => ({ ...prev, isRecording: false }));
      
      if (transcription) {
        await handleSubmitQuestion(transcription);
      }
    } catch (err) {
      console.error('Voice input failed:', err);
      setState(prev => ({
        ...prev,
        isRecording: false,
        error: `Voice input failed: ${err}`,
      }));
    }
  }, [handleSubmitQuestion]);

  // Handle document removal
  const handleRemoveDocument = useCallback(async (name: string) => {
    try {
      await invoke('remove_document', { name });
      setState(prev => ({
        ...prev,
        documents: prev.documents.filter(d => d.name !== name),
      }));
    } catch (err) {
      console.error('Failed to remove document:', err);
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return (
    <div className="h-screen flex flex-col bg-white dark:bg-gray-900">
      {/* Header / Title Bar */}
      <Header />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Document List */}
        <aside className="w-72 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <DocumentList
            documents={state.documents}
            onRemove={handleRemoveDocument}
            isIndexing={state.isIndexing}
          />
          <DropZone onFilesAdded={handleFilesAdded} />
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col">
          <ChatArea
            messages={state.messages}
            isProcessing={state.isProcessing}
          />
          <InputArea
            onSubmit={handleSubmitQuestion}
            onVoiceInput={handleVoiceInput}
            isProcessing={state.isProcessing}
            isRecording={state.isRecording}
            disabled={!state.backendReady}
          />
        </main>
      </div>

      {/* Status Bar */}
      <StatusBar
        backendReady={state.backendReady}
        documentCount={state.documents.filter(d => d.status === 'indexed').length}
        chunkCount={state.documents.reduce((sum, d) => sum + d.chunks, 0)}
        error={state.error}
        onClearError={clearError}
      />
    </div>
  );
}

export default App;
