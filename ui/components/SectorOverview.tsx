'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { apiClient, type SectorData } from '@/lib/api'

export default function SectorOverview() {
  const [sectors, setSectors] = useState<SectorData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSectorData = async () => {
      try {
        setLoading(true)
        setError(null)
        const sectorData = await apiClient.getSectorOverview()
        setSectors(sectorData)
      } catch (err) {
        console.error('Failed to fetch sector data:', err)
        setError('Failed to load sector data. Please try again later.')
      } finally {
        setLoading(false)
      }
    }

    fetchSectorData()
  }, [])

  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-4 h-4 text-green-600" />
    if (change < 0) return <TrendingDown className="w-4 h-4 text-red-600" />
    return <Minus className="w-4 h-4 text-muted-foreground" />
  }

  const getTrendVariant = (change: number): "default" | "secondary" | "destructive" | "outline" => {
    if (change > 0) return 'default'
    if (change < 0) return 'destructive'
    return 'secondary'
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(8)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-4 rounded" />
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <Skeleton className="h-3 w-12" />
                <Skeleton className="h-3 w-16" />
              </div>
              <div className="flex justify-between">
                <Skeleton className="h-3 w-12" />
                <Skeleton className="h-3 w-8" />
              </div>
              <div className="flex justify-between">
                <Skeleton className="h-3 w-12" />
                <Skeleton className="h-3 w-12" />
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

  if (sectors.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center text-muted-foreground">
          <p>No sector data available</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {sectors.map((sector) => (
        <Card key={sector.name} className="hover:shadow-md transition-shadow duration-200 cursor-pointer">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">{sector.name}</CardTitle>
              {getTrendIcon(sector.change)}
            </div>
          </CardHeader>
          
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Change</span>
              <Badge variant={getTrendVariant(sector.change)} className="text-xs">
                {sector.change > 0 ? '+' : ''}{sector.change.toFixed(2)}%
              </Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Stocks</span>
              <span className="text-sm font-medium">{sector.stocks}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Volume</span>
              <span className="text-sm font-medium">{sector.volume}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
