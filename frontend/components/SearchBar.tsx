'use client'

import { useState } from 'react'
import { Search, Sparkles } from 'lucide-react'

interface SearchBarProps {
  onSearch?: (query: string) => void
  placeholder?: string
  className?: string
}

export default function SearchBar({ 
  onSearch, 
  placeholder = "Спросите что-нибудь об инвестициях...",
  className = "" 
}: SearchBarProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && onSearch) {
      onSearch(query.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className={`w-full max-w-3xl mx-auto ${className}`}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
          <Search className="h-6 w-6 text-gray-400" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="block w-full pl-14 pr-14 py-4 text-lg border-2 border-gray-200 rounded-2xl bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-tinkoff-yellow focus:border-transparent shadow-card transition-all hover:shadow-card-hover"
        />
        <div className="absolute inset-y-0 right-0 pr-5 flex items-center">
          <button
            type="submit"
            className="p-2 rounded-lg bg-tinkoff-yellow hover:bg-yellow-400 transition-colors"
            aria-label="Поиск"
          >
            <Sparkles className="h-5 w-5 text-tinkoff-black" />
          </button>
        </div>
      </div>
    </form>
  )
}

