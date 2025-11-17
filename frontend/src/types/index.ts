export interface TelegramSource {
  id: string;
  channelName: string;
  channelUsername: string;
  messageId: number;
  text: string;
  timestamp: string;
  url: string;
  preview?: string;
}

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: TelegramSource[];
  isLoading?: boolean;
}

export interface NewsItem {
  id: string;
  channelName: string;
  channelUsername: string;
  channelAvatar?: string;
  title: string;
  snippet: string;
  timestamp: string;
  url: string;
  category?: string;
}

export interface SearchQuery {
  id: string;
  query: string;
  timestamp: string;
  resultCount: number;
}

