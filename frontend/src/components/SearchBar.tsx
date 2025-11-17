import { useState, FormEvent } from 'react';
import { Search, Sparkles } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
  large?: boolean;
}

export default function SearchBar({ 
  onSearch, 
  placeholder = "Ask about markets, companies, or investments...",
  autoFocus = false,
  large = false
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
      setQuery('');
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className={`relative group ${large ? 'max-w-3xl mx-auto' : ''}`}>
        <div className="absolute inset-0 bg-gradient-to-r from-tbank-yellow/20 to-tbank-yellow/5 rounded-2xl blur-xl group-focus-within:blur-2xl transition-all"></div>
        <div className="relative flex items-center">
          <div className="absolute left-4 text-tbank-gray group-focus-within:text-tbank-yellow transition-colors">
            <Sparkles size={large ? 24 : 20} />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            autoFocus={autoFocus}
            className={`w-full bg-tbank-black-light border-2 border-tbank-gray-dark rounded-2xl text-white placeholder-tbank-gray focus:outline-none focus:border-tbank-yellow transition-all ${
              large ? 'pl-14 pr-16 py-5 text-lg' : 'pl-12 pr-14 py-4'
            }`}
          />
          <button
            type="submit"
            disabled={!query.trim()}
            className={`absolute right-2 bg-tbank-yellow text-tbank-black rounded-xl font-bold transition-all hover:bg-tbank-yellow-dark disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95 ${
              large ? 'px-6 py-3' : 'px-4 py-2'
            }`}
          >
            <Search size={large ? 22 : 18} />
          </button>
        </div>
      </div>
    </form>
  );
}

