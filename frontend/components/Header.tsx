'use client'

import { useState } from 'react'
import { Menu, X, Search } from 'lucide-react'

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-tinkoff-black">
                T<span className="text-tinkoff-yellow">-</span>Plexity
              </span>
            </div>
          </div>

          {/* Desktop Search Bar */}
          <div className="hidden md:flex flex-1 max-w-2xl mx-8">
            <div className="relative w-full">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Спросите что-нибудь об инвестициях..."
                className="block w-full pl-12 pr-4 py-2.5 border border-gray-300 rounded-full bg-gray-50 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-tinkoff-yellow focus:border-transparent transition-all"
              />
            </div>
          </div>

          {/* Desktop Login Button */}
          <div className="hidden md:flex items-center">
            <button className="px-4 py-2 text-sm font-medium text-tinkoff-black hover:text-tinkoff-yellow transition-colors">
              Войти
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-3">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              aria-label="Переключить меню"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Search Bar */}
        <div className="md:hidden pb-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Спросите что-нибудь об инвестициях..."
              className="block w-full pl-12 pr-4 py-2.5 border border-gray-300 rounded-full bg-gray-50 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-tinkoff-yellow focus:border-transparent"
            />
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden pb-4 border-t border-gray-200 pt-4">
            <button className="block w-full text-left px-4 py-2 text-sm font-medium text-tinkoff-black hover:bg-gray-50 rounded-md">
              Войти
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

