'use client'

import { useState } from 'react'
import { Search, Menu, X, TrendingUp, BarChart3, Settings } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')

  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Discover', href: '/discover', icon: TrendingUp },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <header className="bg-background shadow-sm border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-foreground">StockPredict</span>
            </Link>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-full"
                placeholder="Search for stocks, sectors, or companies..."
              />
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-2">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Button key={item.name} variant="ghost" asChild>
                  <Link href={item.href} className="flex items-center space-x-2">
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                </Button>
              )
            })}
          </nav>

          {/* Mobile menu */}
          <div className="md:hidden">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-6 w-6" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right">
                <div className="flex flex-col space-y-4 mt-6">
                  {navigation.map((item) => {
                    const Icon = item.icon
                    return (
                      <Button key={item.name} variant="ghost" asChild className="justify-start">
                        <Link href={item.href} className="flex items-center space-x-2">
                          <Icon className="w-5 h-5" />
                          <span>{item.name}</span>
                        </Link>
                      </Button>
                    )
                  })}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  )
}
