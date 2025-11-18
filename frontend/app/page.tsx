'use client'

import { useState } from 'react'
import Header from '@/components/Header'
import SearchBar from '@/components/SearchBar'
import AnswerCard, { TelegramSource } from '@/components/AnswerCard'
import Footer from '@/components/Footer'
import LoadingSpinner from '@/components/LoadingSpinner'
import { TrendingUp, BarChart3, DollarSign } from 'lucide-react'

const exampleQueries = [
  {
    icon: TrendingUp,
    text: "Какие акции растут сегодня?",
  },
  {
    icon: BarChart3,
    text: "Что происходит с рублем?",
  },
  {
    icon: DollarSign,
    text: "Новости по облигациям",
  },
]

// Mock data for latest answers
const mockAnswers: Array<{
  query: string
  answer: string
  sources: TelegramSource[]
  timestamp: string
}> = [
  {
    query: "Какие акции растут сегодня?",
    answer: "Сегодня наблюдается рост акций технологического сектора. Особенно выделяются компании, связанные с искусственным интеллектом и облачными технологиями. Рост связан с позитивными новостями о внедрении новых продуктов и увеличении инвестиций в сектор.",
    sources: [
      {
        channel: "omyinvestments",
        messageId: 12345,
        preview: "Анализ рынка: технологические акции показывают стабильный рост на фоне новостей о развитии AI...",
        timestamp: "2 часа назад",
        url: "https://t.me/omyinvestments/12345",
      },
      {
        channel: "tb_invest_official",
        messageId: 67890,
        preview: "Обзор торговой сессии: индекс технологий вырос на 2.3%...",
        timestamp: "3 часа назад",
        url: "https://t.me/tb_invest_official/67890",
      },
    ],
    timestamp: "1 час назад",
  },
  {
    query: "Что происходит с рублем?",
    answer: "Рубль демонстрирует стабильность на фоне укрепления нефтяных цен. Центральный банк продолжает политику поддержки курса через валютные интервенции. Эксперты отмечают положительное влияние на инфляционные ожидания.",
    sources: [
      {
        channel: "centralbank_russia",
        messageId: 11111,
        preview: "Официальное заявление ЦБ РФ о текущей валютной политике и стабильности рубля...",
        timestamp: "5 часов назад",
        url: "https://t.me/centralbank_russia/11111",
      },
      {
        channel: "alfa_investments",
        messageId: 22222,
        preview: "Аналитический обзор: динамика курса рубля и прогнозы на ближайшие недели...",
        timestamp: "6 часов назад",
        url: "https://t.me/alfa_investments/22222",
      },
    ],
    timestamp: "2 часа назад",
  },
]

export default function Home() {
  const [answers, setAnswers] = useState(mockAnswers)
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = (query: string) => {
    setIsSearching(true)
    // TODO: Integrate with backend API
    console.log('Searching for:', query)
    // Simulate API call
    setTimeout(() => {
      setIsSearching(false)
    }, 1000)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1 pt-20">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-6xl font-bold text-tinkoff-black mb-6">
              Инвестиционные новости
              <br />
              <span className="text-tinkoff-yellow">в реальном времени</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Получайте мгновенные ответы на вопросы об инвестициях с цитированием источников из Telegram каналов
            </p>
            
            <SearchBar onSearch={handleSearch} className="mb-8" />

            {/* Example Queries */}
            <div className="flex flex-wrap justify-center gap-3 mt-8">
              {exampleQueries.map((example, index) => {
                const Icon = example.icon
                return (
                  <button
                    key={index}
                    onClick={() => handleSearch(example.text)}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-tinkoff-yellow rounded-full text-sm font-medium text-gray-700 hover:text-tinkoff-black transition-colors"
                  >
                    <Icon className="h-4 w-4" />
                    {example.text}
                  </button>
                )
              })}
            </div>
          </div>
        </section>

        {/* Latest Answers Section */}
        {answers.length > 0 && (
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h2 className="text-2xl font-bold text-tinkoff-black mb-6">
              Последние ответы
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {answers.map((answer, index) => (
                <AnswerCard
                  key={index}
                  query={answer.query}
                  answer={answer.answer}
                  sources={answer.sources}
                  timestamp={answer.timestamp}
                />
              ))}
            </div>
          </section>
        )}

        {/* Loading State */}
        {isSearching && (
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <LoadingSpinner message="Ищем ответы..." />
          </section>
        )}
      </main>

      <Footer />
    </div>
  )
}

