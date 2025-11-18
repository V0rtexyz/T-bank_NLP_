import { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { NewsItem } from '../types';
import { Filter, TrendingUp } from 'lucide-react';

export default function NewsFeed() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  
  const categories = [
    { value: 'all', label: 'Все' },
    { value: 'stocks', label: 'Акции' },
    { value: 'crypto', label: 'Крипто' },
    { value: 'forex', label: 'Форекс' },
    { value: 'commodities', label: 'Сырье' },
    { value: 'bonds', label: 'Облигации' }
  ];
  
  useEffect(() => {
    fetchNews();
  }, [filter]);
  
  const fetchNews = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      // Simulating API response for demo
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockNews: NewsItem[] = [
        {
          id: '1',
          channelName: 'Market Watch Pro',
          channelUsername: 'market_watch_pro',
          title: 'Технологические гиганты ведут рост рынка с сильными результатами Q4',
          snippet: 'Крупные технологические компании показали впечатляющие результаты четвертого квартала, подняв NASDAQ до новых высот. Apple, Microsoft и материнская компания Google Alphabet превзошли ожидания аналитиков...',
          timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          url: 'https://t.me/market_watch_pro/12345',
          category: 'stocks',
        },
        {
          id: '2',
          channelName: 'Crypto Insights',
          channelUsername: 'crypto_insights',
          title: 'Bitcoin пробил отметку $45K на новостях об институциональном принятии',
          snippet: 'Bitcoin достиг нового максимума 2024 года сегодня после объявлений трех крупных институтов о своих стратегиях инвестирования в криптовалюты...',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          url: 'https://t.me/crypto_insights/67890',
          category: 'crypto',
        },
        {
          id: '3',
          channelName: 'Investment Daily',
          channelUsername: 'investment_daily',
          title: 'Федеральная резервная система сигнализирует о возможном снижении ставки во Q2',
          snippet: 'Председатель ФРС Пауэлл намекнул на возможные корректировки процентных ставок во время выступления перед Конгрессом, ссылаясь на улучшение показателей инфляции...',
          timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
          url: 'https://t.me/investment_daily/11223',
          category: 'bonds',
        },
        {
          id: '4',
          channelName: 'Trading Signals',
          channelUsername: 'trading_signals',
          title: 'Цены на золото стабилизируются на фоне ослабления доллара',
          snippet: 'Драгоценные металлы показали силу сегодня, золото удерживается выше $2000/унция на фоне снижения индекса доллара...',
          timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
          url: 'https://t.me/trading_signals/44556',
          category: 'commodities',
        },
        {
          id: '5',
          channelName: 'Forex News',
          channelUsername: 'forex_news',
          title: 'EUR/USD пробил ключевой уровень сопротивления',
          snippet: 'Евро укрепился по отношению к доллару сегодня, пробив уровень сопротивления 1.12 впервые за три месяца...',
          timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
          url: 'https://t.me/forex_news/77889',
          category: 'forex',
        },
        {
          id: '6',
          channelName: 'Emerging Markets',
          channelUsername: 'emerging_markets',
          title: 'Азиатские рынки растут на сильных данных по производству',
          snippet: 'Фондовые рынки по всей Азии показали рост после лучших, чем ожидалось, данных PMI по производству из Китая, Японии и Южной Кореи...',
          timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
          url: 'https://t.me/emerging_markets/99000',
          category: 'stocks',
        },
      ];
      
      const filteredNews = filter === 'all' 
        ? mockNews 
        : mockNews.filter(item => item.category === filter);
      
      setNews(filteredNews);
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-12 h-12 bg-tbank-yellow rounded-xl flex items-center justify-center">
              <TrendingUp size={24} className="text-tbank-black" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Последние новости</h1>
              <p className="text-tbank-gray">Обновления в реальном времени из инвестиционных каналов</p>
            </div>
          </div>
          
          {/* Filters */}
          <div className="flex items-center space-x-3 overflow-x-auto pb-2">
            <div className="flex items-center space-x-2 text-tbank-gray flex-shrink-0">
              <Filter size={18} />
              <span className="text-sm font-semibold">Фильтр:</span>
            </div>
            {categories.map(cat => (
              <button
                key={cat.value}
                onClick={() => setFilter(cat.value)}
                className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all flex-shrink-0 ${
                  filter === cat.value
                    ? 'bg-tbank-yellow text-tbank-black'
                    : 'bg-tbank-black-light text-tbank-gray hover:text-white hover:bg-tbank-gray-dark'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>
        
        {/* News Grid */}
        {isLoading ? (
          <LoadingSpinner message="Загрузка последних новостей..." />
        ) : news.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-tbank-gray">Новостей нет для этой категории</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {news.map(item => (
              <NewsCard key={item.id} news={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

