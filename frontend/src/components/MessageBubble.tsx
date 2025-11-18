import { Message } from '../types';
import { User, Sparkles, Loader2 } from 'lucide-react';
import SourceCard from './SourceCard';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const timeAgo = formatDistanceToNow(new Date(message.timestamp), { addSuffix: true, locale: ru });
  
  if (message.type === 'user') {
    return (
      <div className="flex justify-end mb-6">
        <div className="flex items-start space-x-3 max-w-3xl">
          <div className="bg-tbank-yellow text-tbank-black rounded-2xl px-5 py-3">
            <p className="font-medium">{message.content}</p>
          </div>
          <div className="w-10 h-10 bg-tbank-gray-dark rounded-full flex items-center justify-center flex-shrink-0">
            <User size={20} className="text-white" />
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex justify-start mb-8">
      <div className="flex items-start space-x-3 w-full max-w-4xl">
        <div className="w-10 h-10 bg-tbank-yellow rounded-full flex items-center justify-center flex-shrink-0">
          <Sparkles size={20} className="text-tbank-black" />
        </div>
        <div className="flex-1">
          <div className="bg-tbank-black-light rounded-2xl px-5 py-4 mb-3">
            {message.isLoading ? (
              <div className="flex items-center space-x-2 text-tbank-gray">
                <Loader2 size={20} className="animate-spin" />
                <span>Анализ источников...</span>
              </div>
            ) : (
              <>
                <div className="prose prose-invert max-w-none">
                  <p className="text-white leading-relaxed whitespace-pre-wrap">{message.content}</p>
                </div>
                <p className="text-xs text-tbank-gray mt-3">{timeAgo}</p>
              </>
            )}
          </div>
          
          {message.sources && message.sources.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-tbank-gray flex items-center">
                <span className="w-1 h-4 bg-tbank-yellow rounded-full mr-2"></span>
                Источники ({message.sources.length})
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {message.sources.map((source, index) => (
                  <SourceCard key={source.id} source={source} index={index} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

