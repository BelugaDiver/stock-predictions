import SectorOverview from '@/components/SectorOverview'
import StockCards from '@/components/StockCards'
import MarketSummary from '@/components/MarketSummary'

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold mb-4">
          Stock Predictions Dashboard
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Discover trending stocks, analyze market sectors, and make informed investment decisions 
          with our AI-powered insights.
        </p>
      </div>

      {/* Market Summary */}
      <MarketSummary />

      {/* Sector Overview */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Market Sectors</h2>
        <SectorOverview />
      </section>

      {/* Trending Stocks */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Trending Stocks</h2>
        <StockCards />
      </section>
    </div>
  )
}
