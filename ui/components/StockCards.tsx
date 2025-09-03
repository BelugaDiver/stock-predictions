'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Star, ExternalLink, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, type Stock } from '@/lib/api'

export default function StockCards() {
  const [stocks, setStocks] = useState<Stock[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        setLoading(true)
        setError(null)
        const trendingStocks = await apiClient.getTrendingStocks(6)
        setStocks(trendingStocks)
      } catch (err) {
        console.error('Failed to fetch trending stocks:', err)
        setError('Failed to load trending stocks. Please try again later.')
      } finally {
        setLoading(false)
      }
    }

    fetchStocks()
  }, [])

  const getTrendIcon = (change: number) => {
    return change >= 0 ? (
      <TrendingUp className="w-4 h-4 text-green-600" />
    ) : (
      <TrendingDown className="w-4 h-4 text-red-600" />
    )
  }

  const getTrendVariant = (change: number): "default" | "secondary" | "destructive" | "outline" => {
    return change >= 0 ? 'default' : 'destructive'
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-3">
              <div className="flex items-center space-x-3">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="space-y-1">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-6 w-24" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Skeleton className="h-3 w-12" />
                  <Skeleton className="h-4 w-16" />
                </div>
                <div className="space-y-1">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-4 w-12" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2 text-muted-foreground">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      </Card>
    )
  }

  if (stocks.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center text-muted-foreground">
          <p>No trending stocks available</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {stocks.map((stock) => (
        <Card key={stock.symbol} className="group hover:shadow-md transition-shadow duration-200">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <Avatar>
                  <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                    {stock.symbol.slice(0, 2)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="font-semibold text-sm">{stock.symbol}</h3>
                  <p className="text-xs text-muted-foreground truncate max-w-[120px]">{stock.name}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <ExternalLink className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xl font-bold">
                ${stock.price.toFixed(2)}
              </span>
              <div className="flex items-center space-x-2">
                {getTrendIcon(stock.change)}
                <Badge variant={getTrendVariant(stock.change)} className="text-xs">
                  {stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)} ({stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%)
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-muted-foreground">Volume</span>
                <p className="font-medium">{stock.volume}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Market Cap</span>
                <p className="font-medium">{stock.marketCap}</p>
              </div>
            </div>

            <div className="pt-2">
              <Badge variant="outline" className="text-xs">
                {stock.sector}
              </Badge>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
