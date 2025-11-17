import { Zap } from 'lucide-react';

interface QuickQuestionsProps {
  onQuestionClick: (question: string) => void;
}

const questions = [
  "What are the latest market trends?",
  "Tell me about recent IPO news",
  "What's happening with tech stocks?",
  "Recent cryptocurrency updates",
  "Federal Reserve policy changes",
  "Emerging market opportunities",
];

export default function QuickQuestions({ onQuestionClick }: QuickQuestionsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 text-tbank-gray">
        <Zap size={16} className="text-tbank-yellow" />
        <span className="text-sm font-semibold">Quick Questions</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            className="text-left p-4 bg-tbank-black-light border border-tbank-gray-dark rounded-xl hover:border-tbank-yellow hover:shadow-tbank transition-all group"
          >
            <p className="text-sm text-white group-hover:text-tbank-yellow transition-colors">
              {question}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}

