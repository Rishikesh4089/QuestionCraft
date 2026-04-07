import { useState } from 'react';
import { Search, X, FileText, Calendar } from 'lucide-react';

interface SearchPanelProps {
  onClose: () => void;
}

export default function SearchPanel({ onClose }: SearchPanelProps) {
  const [query, setQuery] = useState('');

  const mockResults = [
    { id: '1', title: 'Mathematics Final Exam 2024', date: '2024-01-15', type: 'paper' },
    { id: '2', title: 'Physics Mid-term Template', date: '2024-01-10', type: 'template' },
    { id: '3', title: 'Chemistry Question Bank', date: '2024-01-08', type: 'paper' },
  ];

  const filteredResults = query
    ? mockResults.filter(r => r.title.toLowerCase().includes(query.toLowerCase()))
    : [];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center pt-20 z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl mx-4">
        <div className="p-4 border-b border-slate-200 flex items-center space-x-3">
          <Search className="w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search papers, templates, and more..."
            className="flex-1 outline-none text-lg"
            autoFocus
          />
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-100 rounded transition-colors"
          >
            <X className="w-5 h-5 text-slate-600" />
          </button>
        </div>

        {query && (
          <div className="max-h-96 overflow-y-auto">
            {filteredResults.length > 0 ? (
              <div className="p-2">
                {filteredResults.map((result) => (
                  <button
                    key={result.id}
                    className="w-full flex items-center space-x-3 p-3 hover:bg-slate-50 rounded-lg transition-colors text-left"
                  >
                    <FileText className="w-5 h-5 text-slate-400" />
                    <div className="flex-1 min-w-0">
                      <p className="text-slate-900 font-medium truncate">{result.title}</p>
                      <p className="text-sm text-slate-500 flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>{result.date}</span>
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500">
                No results found for "{query}"
              </div>
            )}
          </div>
        )}

        {!query && (
          <div className="p-8 text-center text-slate-500">
            <Search className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p>Start typing to search papers and templates</p>
          </div>
        )}
      </div>
    </div>
  );
}
