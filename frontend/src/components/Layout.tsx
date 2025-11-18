import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, Newspaper, Clock, MessageSquare } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  
  const navItems = [
    { path: '/', label: 'Главная', icon: Search },
    { path: '/chat', label: 'Чат', icon: MessageSquare },
    { path: '/news', label: 'Новости', icon: Newspaper },
    { path: '/history', label: 'История', icon: Clock },
  ];
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-tbank-gray-dark bg-tbank-black/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="w-10 h-10 bg-tbank-yellow rounded-full flex items-center justify-center transform group-hover:rotate-12 transition-transform">
                <span className="text-tbank-black font-bold text-xl">T</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">
                  T-<span className="text-tbank-yellow">Plexity</span>
                </h1>
                <p className="text-xs text-tbank-gray">Инвестиционная аналитика</p>
              </div>
            </Link>
            
            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                      isActive(item.path)
                        ? 'bg-tbank-yellow text-tbank-black font-semibold'
                        : 'text-tbank-gray hover:text-white hover:bg-tbank-black-light'
                    }`}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
            
            {/* Mobile Menu Button */}
            <button className="md:hidden p-2 rounded-lg hover:bg-tbank-black-light">
              <div className="w-6 h-5 flex flex-col justify-between">
                <span className="block h-0.5 bg-white rounded"></span>
                <span className="block h-0.5 bg-white rounded"></span>
                <span className="block h-0.5 bg-white rounded"></span>
              </div>
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="border-t border-tbank-gray-dark bg-tbank-black-light">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-lg mb-3">T-Plexity</h3>
              <p className="text-tbank-gray text-sm">
                Агрегация новостей об инвестициях в реальном времени на базе ИИ. 
                Будьте в курсе последних рыночных инсайтов.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3">Возможности</h3>
              <ul className="space-y-2 text-sm text-tbank-gray">
                <li className="link-hover cursor-pointer">Новости в реальном времени</li>
                <li className="link-hover cursor-pointer">ИИ-аналитика</li>
                <li className="link-hover cursor-pointer">Прозрачность источников</li>
                <li className="link-hover cursor-pointer">Инвестиционный анализ</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3">Связь</h3>
              <p className="text-tbank-gray text-sm mb-3">
                Создано с использованием современных технологий для финансовых специалистов.
              </p>
              <div className="flex space-x-3">
                <div className="w-8 h-8 bg-tbank-yellow rounded-full flex items-center justify-center cursor-pointer hover:scale-110 transition-transform">
                  <span className="text-tbank-black text-xs font-bold">T</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-tbank-gray-dark text-center text-sm text-tbank-gray">
            <p>© 2025 T-Plexity. Интеллектуальная инвестиционная аналитика.</p>
          </div>
        </div>
      </footer>
      
      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-tbank-black border-t border-tbank-gray-dark z-50">
        <div className="flex justify-around items-center py-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center px-4 py-2 rounded-lg transition-all ${
                  isActive(item.path)
                    ? 'text-tbank-yellow'
                    : 'text-tbank-gray'
                }`}
              >
                <Icon size={22} />
                <span className="text-xs mt-1">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}

