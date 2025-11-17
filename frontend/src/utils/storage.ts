import { SearchQuery } from '../types';

const HISTORY_KEY = 'tplexity_search_history';
const MAX_HISTORY_ITEMS = 50;

/**
 * Get search history from local storage
 */
export function getSearchHistory(): SearchQuery[] {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error reading search history:', error);
    return [];
  }
}

/**
 * Save search query to local storage
 */
export function saveSearchQuery(query: string, resultCount: number): void {
  try {
    const history = getSearchHistory();
    
    const newQuery: SearchQuery = {
      id: Date.now().toString(),
      query,
      timestamp: new Date().toISOString(),
      resultCount,
    };
    
    // Add to beginning and limit size
    const updatedHistory = [newQuery, ...history].slice(0, MAX_HISTORY_ITEMS);
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
  } catch (error) {
    console.error('Error saving search query:', error);
  }
}

/**
 * Delete a specific search query
 */
export function deleteSearchQuery(id: string): void {
  try {
    const history = getSearchHistory();
    const updatedHistory = history.filter(q => q.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
  } catch (error) {
    console.error('Error deleting search query:', error);
  }
}

/**
 * Clear all search history
 */
export function clearSearchHistory(): void {
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch (error) {
    console.error('Error clearing search history:', error);
  }
}

