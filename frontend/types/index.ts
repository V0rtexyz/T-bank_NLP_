export interface TelegramSource {
  channel: string
  messageId: number
  preview: string
  timestamp: string
  url: string
}

export interface Answer {
  id?: string
  query: string
  answer: string
  sources: TelegramSource[]
  timestamp: string
}

export interface SearchResponse {
  query: string
  answer: string
  sources: TelegramSource[]
}


