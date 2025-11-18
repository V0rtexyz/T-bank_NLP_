'use client'

import { MessageCircle, Mail, FileText, ExternalLink } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <h3 className="text-lg font-bold text-tinkoff-black mb-4">
              T<span className="text-tinkoff-yellow">-</span>Plexity
            </h3>
            <p className="text-sm text-gray-600">
              Агрегация инвестиционных новостей в реальном времени с ответами на основе ИИ и источниками из Telegram.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Контакты</h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://t.me/tplexity"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-sm text-gray-600 hover:text-tinkoff-yellow transition-colors"
                >
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Telegram канал
                  <ExternalLink className="h-3 w-3 ml-1" />
                </a>
              </li>
              <li>
                <a
                  href="mailto:support@tplexity.ru"
                  className="flex items-center text-sm text-gray-600 hover:text-tinkoff-yellow transition-colors"
                >
                  <Mail className="h-4 w-4 mr-2" />
                  support@tplexity.ru
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Правовая информация</h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="/policy"
                  className="flex items-center text-sm text-gray-600 hover:text-tinkoff-yellow transition-colors"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Политика конфиденциальности
                </a>
              </li>
              <li>
                <a
                  href="/terms"
                  className="flex items-center text-sm text-gray-600 hover:text-tinkoff-yellow transition-colors"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Условия использования
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} T-Plexity. Все права защищены.
          </p>
        </div>
      </div>
    </footer>
  )
}

