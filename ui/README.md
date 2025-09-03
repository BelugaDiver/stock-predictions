# Stock Predictions Dashboard UI

A modern Next.js frontend for the Stock Predictions API, featuring real-time stock discovery, sector analysis, and market insights.

## Features

- 🚀 **Real-time Stock Data**: Live stock prices and market data
- 📊 **Sector Analysis**: Comprehensive sector performance tracking
- 🔍 **Smart Search**: Intelligent stock and company search
- 📱 **Responsive Design**: Mobile-first responsive interface
- 🎨 **Modern UI**: Clean, professional design with Tailwind CSS
- ⚡ **Fast Performance**: Optimized with Next.js 14 and TypeScript

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **API Integration**: Custom API client for backend communication

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Stock Predictions API running (see main project README)

### Installation

1. Navigate to the UI directory:
```bash
cd ui
```

2. Install dependencies:
```bash
npm install
```

3. Create environment configuration:
```bash
cp .env.example .env.local
```

4. Update environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

5. Start the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
ui/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles and Tailwind utilities
│   ├── layout.tsx         # Root layout component
│   └── page.tsx           # Dashboard page
├── components/            # React components
│   ├── Header.tsx         # Navigation header with search
│   ├── MarketSummary.tsx  # Market overview widget
│   ├── SectorOverview.tsx # Sector performance grid
│   └── StockCards.tsx     # Stock information cards
├── lib/                   # Utilities and API client
│   └── api.ts             # API client for backend communication
├── tailwind.config.js     # Tailwind CSS configuration
├── next.config.js         # Next.js configuration
└── package.json           # Project dependencies
```

## Components

### Header
- Navigation menu with responsive design
- Global search functionality
- Mobile-friendly hamburger menu

### MarketSummary
- Real-time market indices (S&P 500, Dow Jones, NASDAQ, Russell 2000)
- Market status indicator
- Live price changes and percentages

### SectorOverview
- Grid of market sectors with performance metrics
- Visual trend indicators
- Volume and stock count information

### StockCards
- Individual stock information cards
- Price changes with color-coded indicators
- Market cap and volume data
- Sector categorization

## API Integration

The UI connects to the Stock Predictions API through a custom client located in `lib/api.ts`. Key endpoints:

- `/api/discovery/sectors` - Get available sectors
- `/api/discovery/sector-stocks` - Get stocks by sector
- `/api/discovery/search` - Search stocks and companies
- `/api/stocks/{symbol}` - Get individual stock data

## Styling

The project uses Tailwind CSS with a custom configuration:

- **Primary Colors**: Blue-based theme for professional look
- **Success/Danger**: Green/Red for price movements
- **Components**: Reusable component classes for cards, buttons, etc.
- **Responsive**: Mobile-first responsive breakpoints

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Adding New Components

1. Create component in `components/` directory
2. Follow TypeScript conventions with proper typing
3. Use Tailwind classes for styling
4. Import and integrate into relevant pages

### Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API base URL

## Deployment

The application can be deployed to Vercel, Netlify, or any Node.js hosting platform:

1. Build the application:
```bash
npm run build
```

2. Deploy the `out` directory or run in production mode:
```bash
npm start
```

## Integration with Backend

This frontend is designed to work with the Stock Predictions API. Ensure the backend is running and accessible at the URL specified in `NEXT_PUBLIC_API_URL`.

For backend setup instructions, see the main project README.

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for all new code
3. Test responsive design on multiple screen sizes
4. Ensure API integration works correctly

## License

This project is part of the Stock Predictions platform.
