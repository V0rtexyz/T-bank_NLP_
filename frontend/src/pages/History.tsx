import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { SearchQuery } from '../types';
import { Clock, Search, Trash2, ArrowRight } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

export default function History() {
  const navigate = useNavigate();
  const [queries, setQueries] = useState<SearchQuery[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    fetchHistory();
  }, []);
  
  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call or local storage
      // Simulating history for demo
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockHistory: SearchQuery[] = [
        {
          id: '1',
          query: 'What are the latest tech stock trends?',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
          resultCount: 8,
        },
        {
          id: '2',
          query: 'Tell me about recent IPO news',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
          resultCount: 5,
        },
        {
          id: '3',
          query: 'Federal Reserve policy changes',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
          resultCount: 12,
        },
        {
          id: '4',
          query: 'Bitcoin price analysis',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
          resultCount: 15,
        },
        {
          id: '5',
          query: 'European market outlook',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 96).toISOString(),
          resultCount: 7,
        },
      ];
      
      setQueries(mockHistory);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleQueryClick = (query: string) => {
    navigate('/chat', { state: { initialQuery: query } });
  };
  
  const handleDeleteQuery = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setQueries(prev => prev.filter(q => q.id !== id));
    // TODO: Also delete from backend/local storage
  };
  
  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      setQueries([]);
      // TODO: Also clear from backend/local storage
    }
  };
  
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 24) {
      return 'Today';
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
  };
  
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-tbank-yellow rounded-xl flex items-center justify-center">
                <Clock size={24} className="text-tbank-black" />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Search History</h1>
                <p className="text-tbank-gray">Review and re-run your previous queries</p>
              </div>
            </div>
            
            {queries.length > 0 && (
              <button
                onClick={handleClearAll}
                className="btn-secondary flex items-center space-x-2"
              >
                <Trash2 size={18} />
                <span className="hidden md:inline">Clear All</span>
              </button>
            )}
          </div>
          
          {/* Content */}
          {isLoading ? (
            <LoadingSpinner message="Loading history..." />
          ) : queries.length === 0 ? (
            // Empty state
            <div className="text-center py-16">
              <div className="w-20 h-20 bg-tbank-black-light rounded-full flex items-center justify-center mx-auto mb-6">
                <Search size={36} className="text-tbank-gray" />
              </div>
              <h2 className="text-2xl font-bold mb-3">No Search History</h2>
              <p className="text-tbank-gray mb-8">
                Your search history will appear here once you start asking questions
              </p>
              <button
                onClick={() => navigate('/chat')}
                className="btn-primary inline-flex items-center space-x-2"
              >
                <span>Start Searching</span>
                <ArrowRight size={18} />
              </button>
            </div>
          ) : (
            // History list
            <div className="space-y-3">
              {queries.map(query => (
                <div
                  key={query.id}
                  onClick={() => handleQueryClick(query.query)}
                  className="card hover:shadow-tbank-lg cursor-pointer group flex items-center justify-between"
                >
                  <div className="flex-1 min-w-0 mr-4">
                    <div className="flex items-center space-x-3 mb-2">
                      <Search size={18} className="text-tbank-yellow flex-shrink-0" />
                      <h3 className="font-semibold text-white group-hover:text-tbank-yellow transition-colors truncate">
                        {query.query}
                      </h3>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-tbank-gray ml-7">
                      <span>{formatDate(query.timestamp)} at {formatTime(query.timestamp)}</span>
                      <span>•</span>
                      <span>{query.resultCount} sources found</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <button
                      onClick={(e) => handleDeleteQuery(query.id, e)}
                      className="p-2 rounded-lg hover:bg-tbank-gray-dark transition-colors"
                      title="Delete query"
                    >
                      <Trash2 size={18} className="text-tbank-gray hover:text-red-400" />
                    </button>
                    <ArrowRight size={20} className="text-tbank-gray group-hover:text-tbank-yellow transition-colors" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

