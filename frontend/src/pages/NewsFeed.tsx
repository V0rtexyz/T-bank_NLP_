import { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { NewsItem } from '../types';
import { Filter, TrendingUp } from 'lucide-react';

export default function NewsFeed() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  
  const categories = ['all', 'stocks', 'crypto', 'forex', 'commodities', 'bonds'];
  
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
          title: 'Tech Giants Lead Market Rally with Strong Q4 Earnings',
          snippet: 'Major technology companies posted impressive fourth-quarter results, driving the NASDAQ to new highs. Apple, Microsoft, and Google parent Alphabet all exceeded analyst expectations...',
          timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          url: 'https://t.me/market_watch_pro/12345',
          category: 'stocks',
        },
        {
          id: '2',
          channelName: 'Crypto Insights',
          channelUsername: 'crypto_insights',
          title: 'Bitcoin Surges Past $45K on Institutional Adoption News',
          snippet: 'Bitcoin reached a new 2024 high today following announcements from three major institutions about their cryptocurrency investment strategies...',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          url: 'https://t.me/crypto_insights/67890',
          category: 'crypto',
        },
        {
          id: '3',
          channelName: 'Investment Daily',
          channelUsername: 'investment_daily',
          title: 'Federal Reserve Signals Potential Rate Cut in Q2',
          snippet: 'Fed Chairman Powell hinted at possible interest rate adjustments during testimony before Congress, citing improved inflation metrics...',
          timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
          url: 'https://t.me/investment_daily/11223',
          category: 'bonds',
        },
        {
          id: '4',
          channelName: 'Trading Signals',
          channelUsername: 'trading_signals',
          title: 'Gold Prices Stabilize as Dollar Weakens',
          snippet: 'Precious metals showed strength today with gold holding steady above $2,000/oz as the dollar index declined...',
          timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
          url: 'https://t.me/trading_signals/44556',
          category: 'commodities',
        },
        {
          id: '5',
          channelName: 'Forex News',
          channelUsername: 'forex_news',
          title: 'EUR/USD Breaks Key Resistance Level',
          snippet: 'The euro gained ground against the dollar today, breaking through the 1.12 resistance level for the first time in three months...',
          timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
          url: 'https://t.me/forex_news/77889',
          category: 'forex',
        },
        {
          id: '6',
          channelName: 'Emerging Markets',
          channelUsername: 'emerging_markets',
          title: 'Asian Markets Rally on Strong Manufacturing Data',
          snippet: 'Stock markets across Asia posted gains following better-than-expected manufacturing PMI data from China, Japan, and South Korea...',
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
              <h1 className="text-3xl font-bold">Latest News</h1>
              <p className="text-tbank-gray">Real-time updates from investment channels</p>
            </div>
          </div>
          
          {/* Filters */}
          <div className="flex items-center space-x-3 overflow-x-auto pb-2">
            <div className="flex items-center space-x-2 text-tbank-gray flex-shrink-0">
              <Filter size={18} />
              <span className="text-sm font-semibold">Filter:</span>
            </div>
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all flex-shrink-0 ${
                  filter === cat
                    ? 'bg-tbank-yellow text-tbank-black'
                    : 'bg-tbank-black-light text-tbank-gray hover:text-white hover:bg-tbank-gray-dark'
                }`}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>
        </div>
        
        {/* News Grid */}
        {isLoading ? (
          <LoadingSpinner message="Loading latest news..." />
        ) : news.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-tbank-gray">No news available for this category</p>
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

