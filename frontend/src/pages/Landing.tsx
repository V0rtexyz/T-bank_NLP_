import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import QuickQuestions from '../components/QuickQuestions';
import { Zap, Shield, Clock, TrendingUp, Sparkles, ArrowRight } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();
  const [, setQuery] = useState('');
  
  const handleSearch = (query: string) => {
    setQuery(query);
    navigate('/chat', { state: { initialQuery: query } });
  };
  
  const features = [
    {
      icon: Zap,
      title: "Агрегация в реальном времени",
      description: "Свежие публикации из выбранных инвестиционных Telegram-каналов появляются мгновенно в нашей системе."
    },
    {
      icon: Sparkles,
      title: "ИИ-аналитика",
      description: "Задавайте вопросы о рынках, компаниях, экономике. Получайте краткие и точные ответы от нашей LLM."
    },
    {
      icon: Shield,
      title: "Прозрачность источников",
      description: "Каждый ответ включает прямые ссылки на оригинальные сообщения Telegram. Полная прозрачность гарантирована."
    },
    {
      icon: Clock,
      title: "Минимальная задержка",
      description: "Почти мгновенная индексация позволяет запрашивать новости в течение секунд после публикации."
    }
  ];
  
  const stats = [
    { value: "50+", label: "Telegram-каналов" },
    { value: "<30с", label: "Средняя задержка" },
    { value: "24/7", label: "Мониторинг онлайн" },
    { value: "100%", label: "Связано с источниками" }
  ];
  
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-32">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-gradient-to-b from-tbank-yellow/5 to-transparent"></div>
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-tbank-yellow/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-tbank-yellow/5 rounded-full blur-3xl"></div>
        
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <div className="inline-flex items-center space-x-2 bg-tbank-yellow/10 border border-tbank-yellow/20 rounded-full px-4 py-2 mb-6">
              <TrendingUp size={16} className="text-tbank-yellow" />
              <span className="text-sm font-semibold text-tbank-yellow">Платформа инвестиционной аналитики</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Спросите что угодно о
              <br />
              <span className="text-tbank-yellow">Инвестиционных рынках</span>
            </h1>
            
            <p className="text-xl text-tbank-gray-light mb-12 max-w-2xl mx-auto">
              Получайте ИИ-аналитику из Telegram-каналов об инвестициях в реальном времени. 
              Каждый ответ подкреплен прозрачными источниками.
            </p>
            
            {/* Search Bar */}
            <SearchBar onSearch={handleSearch} large autoFocus />
            
            <p className="text-sm text-tbank-gray mt-4">
              Попробуйте спросить: "Какие последние тренды в технологических акциях?" или "Последние обновления политики ФРС"
            </p>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto mb-16">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-tbank-yellow mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-tbank-gray">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
          
          {/* Quick Questions */}
          <div className="max-w-5xl mx-auto">
            <QuickQuestions onQuestionClick={handleSearch} />
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="py-20 bg-tbank-black-light">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Как работает <span className="text-tbank-yellow">T-Plexity</span>
            </h2>
            <p className="text-tbank-gray-light text-lg max-w-2xl mx-auto">
              Объединяем агрегацию данных в реальном времени с продвинутым ИИ для предоставления 
              точной, подкрепленной источниками инвестиционной аналитики.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="card group hover:border-tbank-yellow">
                  <div className="w-12 h-12 bg-tbank-yellow rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Icon size={24} className="text-tbank-black" />
                  </div>
                  <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                  <p className="text-sm text-tbank-gray-light">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="card bg-gradient-to-r from-tbank-black-light to-tbank-gray-dark border-2 border-tbank-yellow/20 text-center p-12">
              <h2 className="text-4xl font-bold mb-4">
                Готовы начать?
              </h2>
              <p className="text-tbank-gray-light text-lg mb-8 max-w-2xl mx-auto">
                Присоединяйтесь к тысячам инвесторов, которые доверяют T-Plexity для получения аналитики рынка в реальном времени.
              </p>
              <button
                onClick={() => navigate('/chat')}
                className="btn-primary inline-flex items-center space-x-2 text-lg"
              >
                <span>Начать задавать вопросы</span>
                <ArrowRight size={20} />
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

