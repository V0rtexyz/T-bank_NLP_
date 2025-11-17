import { Message, TelegramSource, NewsItem, SearchQuery } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface SearchResponse {
  answer: string;
  sources: TelegramSource[];
}

/**
 * Search for investment information using AI
 */
export async function searchQuery(query: string): Promise<SearchResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error searching query:', error);
    throw error;
  }
}

/**
 * Fetch latest news from Telegram channels
 */
export async function fetchNews(category?: string): Promise<NewsItem[]> {
  try {
    const url = category && category !== 'all'
      ? `${API_BASE_URL}/news?category=${category}`
      : `${API_BASE_URL}/news`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error;
  }
}

/**
 * Fetch search history
 */
export async function fetchSearchHistory(): Promise<SearchQuery[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/history`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching history:', error);
    throw error;
  }
}

/**
 * Save search query to history
 */
export async function saveSearchQuery(query: string, resultCount: number): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/history`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, resultCount }),
    });
  } catch (error) {
    console.error('Error saving search query:', error);
    // Non-critical, don't throw
  }
}

/**
 * Delete search query from history
 */
export async function deleteSearchQuery(id: string): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/history/${id}`, {
      method: 'DELETE',
    });
  } catch (error) {
    console.error('Error deleting search query:', error);
    throw error;
  }
}

/**
 * Clear all search history
 */
export async function clearSearchHistory(): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/history`, {
      method: 'DELETE',
    });
  } catch (error) {
    console.error('Error clearing search history:', error);
    throw error;
  }
}

