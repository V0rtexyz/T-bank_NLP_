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
    { path: '/', label: 'Home', icon: Search },
    { path: '/chat', label: 'Chat', icon: MessageSquare },
    { path: '/news', label: 'News', icon: Newspaper },
    { path: '/history', label: 'History', icon: Clock },
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
                <p className="text-xs text-tbank-gray">Investment Intelligence</p>
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
                Real-time investment news aggregation powered by AI. 
                Stay informed with the latest market insights.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3">Features</h3>
              <ul className="space-y-2 text-sm text-tbank-gray">
                <li className="link-hover cursor-pointer">Real-time News</li>
                <li className="link-hover cursor-pointer">AI-Powered Insights</li>
                <li className="link-hover cursor-pointer">Source Transparency</li>
                <li className="link-hover cursor-pointer">Investment Analysis</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-3">Connect</h3>
              <p className="text-tbank-gray text-sm mb-3">
                Built with modern technology for financial professionals.
              </p>
              <div className="flex space-x-3">
                <div className="w-8 h-8 bg-tbank-yellow rounded-full flex items-center justify-center cursor-pointer hover:scale-110 transition-transform">
                  <span className="text-tbank-black text-xs font-bold">T</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-tbank-gray-dark text-center text-sm text-tbank-gray">
            <p>© 2025 T-Plexity. Intelligent Investment Intelligence.</p>
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

