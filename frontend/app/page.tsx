/**
 * Product Hunter AI - Dashboard Home Page
 * Overview of market intelligence
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import {
  TrendingUp,
  AlertTriangle,
  Database,
  Users,
  BarChart3,
  Clock,
  CheckCircle,
} from 'lucide-react'
import { fetcher } from '@/lib/api'

async function getDashboardData() {
  // This would fetch from the backend API
  return {
    totalProducts: 1247,
    opportunities: 42,
    sources: 8,
    healthySources: 7,
    lastRun: '2 hours ago',
    nextRun: '22:00',
    topCategory: 'Smart Gadgets',
    confidence: 92,
  }
}

export default async function DashboardPage() {
  const data = await getDashboardData()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Overview</h2>
          <p className="text-gray-600 mt-1">
            Egyptian Electronics Market Intelligence Dashboard
          </p>
        </div>
        <Link href="/opportunities">
          <Button>
            <TrendingUp className="h-4 w-4 mr-2" />
            View Opportunities
          </Button>
        </Link>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <Database className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.totalProducts}</div>
            <p className="text-xs text-green-600">+15% from last week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Opportunities</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.opportunities}</div>
            <p className="text-xs text-gray-600">High-profit products identified</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sources</CardTitle>
            <Users className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.healthySources}/{data.sources}
            </div>
            <p className="text-xs text-gray-600">
              {data.healthySources === data.sources ? 'All sources healthy' : 'Some sources degraded'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Run</CardTitle>
            <Clock className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.lastRun}</div>
            <p className="text-xs text-gray-600">Next run: {data.nextRun}</p>
          </CardContent>
        </Card>
      </div>

      {/* Confidence and Top Category */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Product Confidence</CardTitle>
            <CardDescription>Based on data quality and completeness</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="text-4xl font-bold text-green-600">{data.confidence}%</div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Data Completeness</span>
                <span>95%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Source Quality</span>
                <span>92%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Market Freshness</span>
                <span>88%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Category</CardTitle>
            <CardDescription>Most opportunities identified</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-2xl font-bold">{data.topCategory}</div>
            <p className="text-sm text-gray-600">
              This category has the highest scoring opportunities
            </p>
            <Link href="/trending?category={data.topCategory}">
              <Button variant="outline" size="sm">
                View Category Insights
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks for market analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/opportunities">
              <Button variant="outline" className="w-full justify-start">
                <BarChart3 className="h-4 w-4 mr-2" />
                Top Opportunities
              </Button>
            </Link>
            <Link href="/suppliers">
              <Button variant="outline" className="w-full justify-start">
                <Users className="h-4 w-4 mr-2" />
                Supplier Directory
              </Button>
            </Link>
            <Link href="/reports/today">
              <Button variant="outline" className="w-full justify-start">
                <Clock className="h-4 w-4 mr-2" />
                Today's Report
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}