# T-Plexity Frontend

Modern web interface for T-Plexity — an intelligent system that aggregates and analyzes investment Telegram news in real-time.

## 🎨 Design Philosophy

T-Plexity combines the clean, minimalist interface of Perplexity with T-Bank's bold yellow-black color scheme and fintech sophistication. The result is a professional, reliable platform for investment intelligence.

### Design Principles
- **Minimalism**: Clean layouts, focus on content
- **Perplexity-inspired**: Search-first UX, transparent sources
- **T-Bank aesthetics**: Yellow-black palette, bold typography, structured blocks
- **Responsive**: Mobile-first design that works everywhere

## ✨ Features

### Core Functionality
- 🔍 **Intelligent Search**: AI-powered Q&A about markets, companies, and investments
- 📰 **Real-time News Feed**: Fresh Telegram channel aggregation
- 💬 **Chat Interface**: Conversational AI with source transparency
- 📚 **Search History**: Track and re-run previous queries
- 🔗 **Source Linking**: Direct links to original Telegram messages

### UI Components
- **Landing Page**: Hero section with search bar and quick questions
- **Chat View**: Message bubbles with AI responses and source cards
- **News Feed**: Categorized news cards with filtering
- **History**: Query management and re-search functionality

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Backend API running (see main README)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Update .env with your API URL
# VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

## 🏗️ Project Structure

```
frontend/
├── public/               # Static assets
│   └── favicon.svg      # T-Bank themed favicon
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Layout.tsx           # App layout with header/footer
│   │   ├── SearchBar.tsx        # Main search input
│   │   ├── MessageBubble.tsx    # Chat message display
│   │   ├── SourceCard.tsx       # Telegram source cards
│   │   ├── NewsCard.tsx         # News item cards
│   │   ├── QuickQuestions.tsx   # Suggested queries
│   │   └── LoadingSpinner.tsx   # Loading state
│   ├── pages/           # Main application pages
│   │   ├── Landing.tsx          # Home page
│   │   ├── Chat.tsx             # AI chat interface
│   │   ├── NewsFeed.tsx         # News aggregation
│   │   └── History.tsx          # Search history
│   ├── types/           # TypeScript interfaces
│   │   └── index.ts             # Shared types
│   ├── utils/           # Helper functions
│   │   ├── api.ts               # API client functions
│   │   └── storage.ts           # Local storage utilities
│   ├── App.tsx          # Main app component with routing
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles and Tailwind
├── index.html           # HTML template
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── vite.config.ts       # Vite build configuration
```

## 🎨 Styling System

### T-Bank Color Palette
```css
tbank-yellow:       #FFDD2D  /* Primary accent */
tbank-yellow-dark:  #FFD700  /* Hover states */
tbank-black:        #1F1F1F  /* Background */
tbank-black-light:  #2A2A2A  /* Cards, inputs */
tbank-gray:         #9E9E9E  /* Secondary text */
tbank-gray-light:   #E0E0E0  /* Borders */
```

### Utility Classes
- `btn-primary`: Yellow button with hover effects
- `btn-secondary`: Dark button with border
- `card`: Standard card container
- `input-field`: Styled form input
- `link-hover`: Yellow hover transition

### Custom Components
All components follow T-Bank design language:
- Rounded corners (rounded-xl, rounded-2xl)
- Yellow accent highlights
- Subtle shadows and hover effects
- Bold, confident typography

## 🔌 API Integration

The frontend connects to the backend API for:

### Endpoints Used
- `POST /api/search` - AI-powered search queries
- `GET /api/news` - Fetch latest news (with category filter)
- `GET /api/history` - Retrieve search history
- `POST /api/history` - Save search query
- `DELETE /api/history/:id` - Delete specific query
- `DELETE /api/history` - Clear all history

### Mock Data
Demo mode included with mock data for testing UI without backend. See:
- `src/pages/Chat.tsx` - Mock AI responses
- `src/pages/NewsFeed.tsx` - Mock news items
- `src/pages/History.tsx` - Mock search history

## 📱 Responsive Design

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Mobile Features
- Fixed bottom navigation bar
- Collapsible menu
- Touch-optimized buttons
- Responsive grid layouts

## 🔧 Configuration

### Environment Variables
Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api
```

### Vite Configuration
- API proxy to backend
- Path aliases (@/ for src/)
- React plugin with Fast Refresh

### Tailwind Configuration
- Custom T-Bank color scheme
- Extended shadows
- Animation utilities

## 🧪 Development

### Available Scripts
```bash
npm run dev      # Start dev server
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Code Style
- TypeScript strict mode
- ESLint with React hooks rules
- Functional components with hooks
- Clear prop interfaces

### Component Guidelines
1. **Props**: Define clear TypeScript interfaces
2. **State**: Use appropriate hooks (useState, useEffect)
3. **Styling**: Tailwind classes with custom utilities
4. **Accessibility**: Semantic HTML, ARIA labels
5. **Performance**: Lazy loading, code splitting

## 🚢 Deployment

### Build Output
```bash
npm run build
# Creates dist/ folder with optimized assets
```

### Deployment Platforms
- **Vercel**: Connect GitHub repo, auto-deploy
- **Netlify**: Drag-and-drop dist/ folder
- **AWS S3 + CloudFront**: Static hosting
- **Docker**: Use nginx to serve dist/

### Example Dockerfile
```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🎯 Future Enhancements

### Planned Features
- [ ] Dark/Light theme toggle
- [ ] User authentication
- [ ] Personalized news feeds
- [ ] Advanced filtering options
- [ ] Export chat transcripts
- [ ] Keyboard shortcuts
- [ ] Multi-language support
- [ ] PWA capabilities

### Performance Optimizations
- [ ] Virtual scrolling for long lists
- [ ] Image lazy loading
- [ ] Route-based code splitting
- [ ] Service worker caching

## 🐛 Troubleshooting

### Common Issues

**Port 3000 already in use**
```bash
# Change port in vite.config.ts or:
PORT=3001 npm run dev
```

**API connection errors**
- Verify backend is running
- Check VITE_API_URL in .env
- Ensure CORS is configured on backend

**Tailwind styles not working**
- Restart dev server after config changes
- Check content paths in tailwind.config.js

**Type errors**
- Run `npm install` to update dependencies
- Clear node_modules and reinstall if needed

## 📄 License

This project is part of the T-Plexity system. See main repository for license information.

## 🤝 Contributing

1. Follow existing code style
2. Use TypeScript types
3. Test responsive design
4. Update documentation
5. Follow T-Bank design system

## 📞 Support

For issues or questions:
- Open GitHub issue
- Check main T-Plexity documentation
- Review Vite/React documentation

---

Built with ❤️ using React, TypeScript, and Tailwind CSS

