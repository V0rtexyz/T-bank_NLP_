import { ExternalLink, Clock } from 'lucide-react';
import { TelegramSource } from '../types';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

interface SourceCardProps {
  source: TelegramSource;
  index: number;
}

export default function SourceCard({ source, index }: SourceCardProps) {
  const timeAgo = formatDistanceToNow(new Date(source.timestamp), { addSuffix: true, locale: ru });
  
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block group"
    >
      <div className="card hover:shadow-tbank-lg hover:scale-[1.02] transition-all">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="flex items-center justify-center w-6 h-6 bg-tbank-yellow text-tbank-black rounded-full text-xs font-bold">
              {index + 1}
            </span>
            <div>
              <h4 className="font-semibold text-white group-hover:text-tbank-yellow transition-colors">
                {source.channelName}
              </h4>
              <p className="text-xs text-tbank-gray">@{source.channelUsername}</p>
            </div>
          </div>
          <ExternalLink size={16} className="text-tbank-gray group-hover:text-tbank-yellow transition-colors" />
        </div>
        
        <p className="text-sm text-tbank-gray-light line-clamp-3 mb-3">
          {source.preview || source.text}
        </p>
        
        <div className="flex items-center text-xs text-tbank-gray">
          <Clock size={12} className="mr-1" />
          {timeAgo}
        </div>
      </div>
    </a>
  );
}

