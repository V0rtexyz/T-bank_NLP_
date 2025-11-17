# T-Plexity Design System

## Overview

T-Plexity's design combines the minimalist, search-focused UX of Perplexity with T-Bank's bold, professional fintech aesthetic. The result is a clean, reliable interface that conveys technological sophistication while maintaining ease of use.

## Design Principles

### 1. Minimalism First
- Clean layouts with generous whitespace
- Focus on content and functionality
- Remove unnecessary decorative elements
- Clear visual hierarchy

### 2. Source Transparency
- Every AI answer shows its sources
- Direct links to Telegram messages
- Clear attribution for all information
- Perplexity-style source cards

### 3. Fintech Sophistication
- Professional, trustworthy appearance
- Bold typography typical of financial services
- Structured, organized information blocks
- T-Bank's signature yellow-black palette

### 4. Speed & Efficiency
- Fast loading times
- Instant search responses
- Minimal animations (purposeful only)
- Real-time data updates

## Color System

### Primary Colors

#### T-Bank Yellow
```css
--tbank-yellow: #FFDD2D;
--tbank-yellow-dark: #FFD700;
```
**Usage**: Primary actions, accents, highlights, branding elements

#### T-Bank Black
```css
--tbank-black: #1F1F1F;
--tbank-black-light: #2A2A2A;
```
**Usage**: Backgrounds, cards, input fields

### Secondary Colors

#### Gray Scale
```css
--tbank-gray: #9E9E9E;
--tbank-gray-light: #E0E0E0;
--tbank-gray-dark: #424242;
```
**Usage**: Secondary text, borders, disabled states

### Semantic Colors
- **Success**: Use yellow with positive messaging
- **Warning**: Orange tints (#FFB84D)
- **Error**: Red (#FF4444)
- **Info**: Light blue accents (#4DABF7)

## Typography

### Font Family
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

Inter provides excellent readability and a modern, professional appearance suitable for financial applications.

### Type Scale

#### Headings
- **H1**: 3rem (48px) / Bold / Leading tight
- **H2**: 2.25rem (36px) / Bold / Leading tight
- **H3**: 1.5rem (24px) / Semibold / Leading snug
- **H4**: 1.25rem (20px) / Semibold / Leading normal

#### Body
- **Large**: 1.125rem (18px) / Regular / Leading relaxed
- **Base**: 1rem (16px) / Regular / Leading normal
- **Small**: 0.875rem (14px) / Regular / Leading normal
- **Tiny**: 0.75rem (12px) / Regular / Leading tight

### Font Weights
- **Light**: 300 (rarely used)
- **Regular**: 400 (body text)
- **Medium**: 500 (emphasis)
- **Semibold**: 600 (subheadings)
- **Bold**: 700 (headings, buttons)
- **Extra Bold**: 800 (hero text)

## Spacing System

### Base Unit: 4px (0.25rem)

```css
spacing-1: 0.25rem;  /* 4px */
spacing-2: 0.5rem;   /* 8px */
spacing-3: 0.75rem;  /* 12px */
spacing-4: 1rem;     /* 16px */
spacing-5: 1.25rem;  /* 20px */
spacing-6: 1.5rem;   /* 24px */
spacing-8: 2rem;     /* 32px */
spacing-10: 2.5rem;  /* 40px */
spacing-12: 3rem;    /* 48px */
spacing-16: 4rem;    /* 64px */
spacing-20: 5rem;    /* 80px */
```

## Border Radius

### Rounded Corners
```css
rounded-sm: 0.25rem;   /* 4px - small elements */
rounded: 0.5rem;       /* 8px - buttons, tags */
rounded-lg: 0.75rem;   /* 12px - inputs */
rounded-xl: 1rem;      /* 16px - cards, containers */
rounded-2xl: 1.5rem;   /* 24px - large cards */
rounded-full: 9999px;  /* Pills, avatars */
```

T-Bank style prefers more rounded corners (xl, 2xl) for a modern, friendly appearance.

## Shadows

### Elevation System

```css
/* Subtle hover effect */
shadow-tbank: 0 4px 16px rgba(255, 221, 45, 0.1);

/* Prominent hover state */
shadow-tbank-lg: 0 8px 32px rgba(255, 221, 45, 0.15);

/* Standard card shadow */
shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);

/* Deep shadow for modals */
shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
```

Use yellow-tinted shadows for T-Bank branding, standard dark shadows for elevation.

## Components

### Buttons

#### Primary Button
- Background: tbank-yellow
- Text: tbank-black
- Font: Bold
- Padding: 12px 24px
- Border radius: rounded-xl
- Hover: scale-105, bg-yellow-dark
- Shadow: shadow-tbank

#### Secondary Button
- Background: tbank-black-light
- Text: white
- Border: 1px solid gray-dark
- Padding: 12px 24px
- Border radius: rounded-xl
- Hover: bg-gray-dark

### Cards

#### Standard Card
- Background: tbank-black-light
- Border: 1px solid gray-dark
- Border radius: rounded-2xl
- Padding: 24px
- Hover: border-yellow/30, shadow-tbank-lg

#### Source Card
- Smaller padding: 20px
- Yellow accent number badge
- External link icon
- Truncated text with line-clamp

### Inputs

#### Search Bar
- Background: tbank-black-light
- Border: 2px solid gray-dark
- Border radius: rounded-2xl
- Padding: 16px 24px
- Focus: border-yellow, ring-yellow/20
- Icon: Sparkles (left), Search button (right)

### Navigation

#### Header
- Fixed position, backdrop blur
- Border bottom: gray-dark
- Logo with yellow accent
- Active state: yellow background

#### Bottom Nav (Mobile)
- Fixed bottom position
- Icon + label layout
- Yellow accent for active state

## Layouts

### Container Widths
- **Max Width**: 1280px (container)
- **Content Width**: 896px (prose, chat)
- **Search Width**: 768px (search bars)

### Grid System
```css
/* News feed, features */
grid-cols-1 md:grid-cols-2 lg:grid-cols-3

/* Stats, quick questions */
grid-cols-2 md:grid-cols-4

/* Source cards */
grid-cols-1 md:grid-cols-2
```

### Responsive Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## Animations

### Transitions
```css
transition-all duration-200  /* Standard */
transition-colors duration-150  /* Text colors */
transition-transform  /* Scale, rotate */
```

### Hover Effects
- **Scale up**: hover:scale-105 (buttons)
- **Scale down**: active:scale-95 (buttons)
- **Color change**: hover:text-yellow, hover:border-yellow
- **Glow**: Yellow shadow on focus

### Loading States
- Spinner: rotate animation
- Shimmer: gradient slide animation
- Pulse: slow opacity pulse

## Icons

### Icon Library
**Lucide React** - Clean, consistent, professional icons

### Common Icons
- Search: Magnifying glass
- Sparkles: AI/magic
- TrendingUp: Markets, growth
- Clock: Time, history
- ExternalLink: Source links
- Filter: Filtering
- User: Profile
- Send: Submit, send message

### Icon Sizing
- Small: 16px
- Medium: 20px
- Large: 24px
- Hero: 36px+

## Page Layouts

### Landing Page
1. **Hero Section**: Large search bar, headline, quick questions
2. **Stats Bar**: Key metrics in yellow
3. **Features Grid**: 4-column icon cards
4. **CTA Section**: Final conversion element

### Chat Page
1. **Empty State**: Centered search with suggestions
2. **Chat View**: Message bubbles + source cards
3. **Fixed Input**: Bottom-fixed search bar

### News Feed
1. **Header**: Title + category filters
2. **Grid Layout**: Responsive news cards
3. **Pagination**: Load more on scroll

### History
1. **Header**: Title + clear all button
2. **List View**: Query cards with metadata
3. **Empty State**: Call to action

## Mobile Considerations

### Touch Targets
- Minimum size: 44x44px
- Increased padding on mobile
- Larger tap areas for links

### Mobile Navigation
- Bottom fixed nav bar
- 4 main sections
- Icon + label for clarity

### Mobile Typography
- Slightly smaller font sizes
- Adjusted line heights
- More compact spacing

## Accessibility

### Color Contrast
- Yellow on black: AAA rating
- White on black: AAA rating
- Gray text: AA minimum

### Focus States
- Yellow ring on focus
- Clear keyboard navigation
- Skip to content link

### Semantic HTML
- Proper heading hierarchy
- ARIA labels where needed
- Alt text for images

## Brand Guidelines

### Logo Usage
- Yellow circle with black "T"
- Can be used as standalone icon
- Maintain aspect ratio
- Minimum size: 32x32px

### Voice & Tone
- **Professional**: Financial expertise
- **Confident**: Bold statements
- **Clear**: No jargon
- **Helpful**: User-focused

### Imagery
- Abstract yellow/black graphics
- Financial charts and graphs
- Minimal photography
- Iconography over photos

## Implementation Notes

### CSS Strategy
- Tailwind utility classes
- Custom components in index.css
- Minimal custom CSS
- Consistent naming

### Component Structure
- Functional components
- TypeScript for props
- Reusable, composable
- Clear prop interfaces

### State Management
- React hooks (useState, useEffect)
- Context for global state (if needed)
- Local storage for persistence
- API calls in utils/api.ts

---

This design system ensures consistency across the T-Plexity platform while maintaining the perfect balance between Perplexity's minimalism and T-Bank's bold fintech aesthetic.

