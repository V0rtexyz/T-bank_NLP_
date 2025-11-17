import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import MessageBubble from '../components/MessageBubble';
import QuickQuestions from '../components/QuickQuestions';
import { Message, TelegramSource } from '../types';
import { Send } from 'lucide-react';

export default function Chat() {
  const location = useLocation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  useEffect(() => {
    // Handle initial query from landing page
    const initialQuery = (location.state as any)?.initialQuery;
    if (initialQuery) {
      handleSearch(initialQuery);
      // Clear the state to prevent re-sending on refresh
      window.history.replaceState({}, document.title);
    }
  }, [location]);
  
  const handleSearch = async (query: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    // Add loading assistant message
    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isLoading: true,
    };
    
    setMessages(prev => [...prev, loadingMessage]);
    
    try {
      // TODO: Replace with actual API call
      // Simulating API response for demo
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock response with sources
      const mockSources: TelegramSource[] = [
        {
          id: '1',
          channelName: 'Investment Insights',
          channelUsername: 'invest_insights',
          messageId: 12345,
          text: 'Major tech stocks showing bullish signals as market rebounds...',
          timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          url: 'https://t.me/invest_insights/12345',
          preview: 'Major tech stocks showing bullish signals as market rebounds...',
        },
        {
          id: '2',
          channelName: 'Market Analysis',
          channelUsername: 'market_analysis',
          messageId: 67890,
          text: 'Tech sector ETFs gained 2.3% today following positive earnings reports...',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          url: 'https://t.me/market_analysis/67890',
          preview: 'Tech sector ETFs gained 2.3% today following positive earnings...',
        },
        {
          id: '3',
          channelName: 'Financial News',
          channelUsername: 'fin_news',
          messageId: 11223,
          text: 'NASDAQ composite up 1.8%, driven primarily by semiconductor stocks...',
          timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
          url: 'https://t.me/fin_news/11223',
          preview: 'NASDAQ composite up 1.8%, driven primarily by semiconductor...',
        },
        {
          id: '4',
          channelName: 'Tech Investor',
          channelUsername: 'tech_investor',
          messageId: 44556,
          text: 'AI companies leading the charge with strong Q4 performance metrics...',
          timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
          url: 'https://t.me/tech_investor/44556',
          preview: 'AI companies leading the charge with strong Q4 performance...',
        },
      ];
      
      const assistantMessage: Message = {
        id: loadingMessage.id,
        type: 'assistant',
        content: `Based on recent market analysis, tech stocks are currently showing strong positive momentum. The NASDAQ composite has risen 1.8%, with semiconductor and AI-focused companies leading the gains.\n\nKey highlights:\n• Major tech ETFs gained 2.3% following positive earnings reports\n• AI companies demonstrated particularly strong Q4 performance\n• Semiconductor stocks are driving significant market gains\n• Overall bullish signals across the technology sector\n\nThis trend appears to be supported by solid fundamentals and positive investor sentiment toward innovation-focused companies.`,
        timestamp: new Date().toISOString(),
        sources: mockSources,
        isLoading: false,
      };
      
      setMessages(prev => prev.map(msg => 
        msg.id === loadingMessage.id ? assistantMessage : msg
      ));
    } catch (error) {
      console.error('Error fetching response:', error);
      // Handle error
      setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id));
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen pb-24 md:pb-8">
      <div className="container mx-auto px-4 py-8">
        {messages.length === 0 ? (
          // Empty state
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12 pt-12">
              <div className="w-20 h-20 bg-tbank-yellow rounded-full flex items-center justify-center mx-auto mb-6">
                <Send size={36} className="text-tbank-black" />
              </div>
              <h1 className="text-4xl font-bold mb-4">
                Ask <span className="text-tbank-yellow">T-Plexity</span>
              </h1>
              <p className="text-tbank-gray-light text-lg">
                Get AI-powered insights from real-time investment news
              </p>
            </div>
            
            <div className="mb-8">
              <SearchBar onSearch={handleSearch} large autoFocus />
            </div>
            
            <QuickQuestions onQuestionClick={handleSearch} />
          </div>
        ) : (
          // Chat view
          <div className="max-w-5xl mx-auto">
            {/* Messages */}
            <div className="mb-8 space-y-6">
              {messages.map(message => (
                <MessageBubble key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            {/* Fixed search bar at bottom */}
            <div className="fixed bottom-20 md:bottom-8 left-0 right-0 bg-gradient-to-t from-tbank-black via-tbank-black to-transparent pt-6 pb-6">
              <div className="container mx-auto px-4">
                <div className="max-w-4xl mx-auto">
                  <SearchBar
                    onSearch={handleSearch}
                    placeholder="Ask a follow-up question..."
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

