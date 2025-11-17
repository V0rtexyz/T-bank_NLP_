import { ExternalLink, Clock, TrendingUp } from 'lucide-react';
import { NewsItem } from '../types';
import { formatDistanceToNow } from 'date-fns';

interface NewsCardProps {
  news: NewsItem;
}

export default function NewsCard({ news }: NewsCardProps) {
  const timeAgo = formatDistanceToNow(new Date(news.timestamp), { addSuffix: true });
  
  return (
    <a
      href={news.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block group"
    >
      <div className="card hover:shadow-tbank-lg hover:scale-[1.01] transition-all h-full">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-tbank-yellow rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-tbank-black font-bold text-lg">
                {news.channelName.charAt(0)}
              </span>
            </div>
            <div>
              <h4 className="font-semibold text-white">
                {news.channelName}
              </h4>
              <p className="text-xs text-tbank-gray">@{news.channelUsername}</p>
            </div>
          </div>
          <ExternalLink size={18} className="text-tbank-gray group-hover:text-tbank-yellow transition-colors" />
        </div>
        
        {news.category && (
          <div className="inline-flex items-center space-x-1 bg-tbank-yellow/10 text-tbank-yellow px-3 py-1 rounded-full text-xs font-semibold mb-3">
            <TrendingUp size={12} />
            <span>{news.category}</span>
          </div>
        )}
        
        <h3 className="font-bold text-lg text-white mb-3 group-hover:text-tbank-yellow transition-colors line-clamp-2">
          {news.title}
        </h3>
        
        <p className="text-sm text-tbank-gray-light mb-4 line-clamp-3">
          {news.snippet}
        </p>
        
        <div className="flex items-center text-xs text-tbank-gray pt-3 border-t border-tbank-gray-dark">
          <Clock size={12} className="mr-1" />
          {timeAgo}
        </div>
      </div>
    </a>
  );
}

