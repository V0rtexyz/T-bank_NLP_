'use client'

import { ExternalLink, MessageSquare, Clock } from 'lucide-react'

export interface TelegramSource {
  channel: string
  messageId: number
  preview: string
  timestamp: string
  url: string
}

export interface AnswerCardProps {
  query: string
  answer: string
  sources: TelegramSource[]
  timestamp?: string
}

export default function AnswerCard({ query, answer, sources, timestamp }: AnswerCardProps) {
  return (
    <article className="bg-white rounded-2xl shadow-card hover:shadow-card-hover transition-shadow p-6 md:p-8">
      {/* Query */}
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-tinkoff-black mb-2">{query}</h2>
        {timestamp && (
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="h-4 w-4 mr-1" />
            <span>{timestamp}</span>
          </div>
        )}
      </div>

      {/* Answer */}
      <div className="prose prose-sm max-w-none mb-6">
        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{answer}</p>
      </div>

      {/* Sources */}
      {sources && sources.length > 0 && (
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 flex items-center">
            <MessageSquare className="h-4 w-4 mr-2" />
            Источники ({sources.length})
          </h3>
          <div className="space-y-3">
            {sources.map((source, index) => (
              <a
                key={index}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-tinkoff-black">
                        {source.channel}
                      </span>
                      <span className="text-xs text-gray-500">#{source.messageId}</span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2 group-hover:text-gray-900">
                      {source.preview}
                    </p>
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-tinkoff-yellow flex-shrink-0 mt-1 transition-colors" />
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </article>
  )
}


