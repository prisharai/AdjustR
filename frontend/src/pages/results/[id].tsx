import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { getResults, ResultsResponse } from '@/services/api'
import FilterPanel, { FilterOptions } from '@/components/FilterPanel'
import FrameGallery from '@/components/FrameGallery'
import VideoPlayer from '@/components/VideoPlayer'
import DamageChart from '@/components/DamageChart'

type ViewMode = 'overview' | 'gallery' | 'table' | 'charts'

export default function Results() {
  const router = useRouter()
  const { id } = router.query
  const [results, setResults] = useState<ResultsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('overview')
  const [filters, setFilters] = useState<FilterOptions>({
    damageTypes: [],
    severities: [],
    minConfidence: 0,
    sortBy: 'frame_number',
    sortOrder: 'asc'
  })

  useEffect(() => {
    if (id) {
      fetchResults()
    }
  }, [id])

  const fetchResults = async () => {
    try {
      setLoading(true)
      const data = await getResults(Number(id))
      setResults(data)
    } catch (err: any) {
      console.error('Error fetching results:', err)
      setError(err.message || 'Failed to load results')
    } finally {
      setLoading(false)
    }
  }

  // Apply filters to inferences
  const getFilteredInferences = () => {
    if (!results) return []

    let filtered = results.inferences

    // Filter by damage type
    if (filters.damageTypes.length > 0) {
      filtered = filtered.filter(inf => filters.damageTypes.includes(inf.damage_type))
    }

    // Filter by severity
    if (filters.severities.length > 0) {
      filtered = filtered.filter(inf => filters.severities.includes(inf.severity as any))
    }

    // Filter by confidence
    if (filters.minConfidence > 0) {
      filtered = filtered.filter(inf => inf.confidence * 100 >= filters.minConfidence)
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0
      switch (filters.sortBy) {
        case 'frame_number':
          comparison = a.frame_number - b.frame_number
          break
        case 'confidence':
          comparison = a.confidence - b.confidence
          break
        case 'severity':
          const severityOrder = { high: 3, medium: 2, low: 1 }
          comparison = (severityOrder[a.severity as keyof typeof severityOrder] || 0) -
                      (severityOrder[b.severity as keyof typeof severityOrder] || 0)
          break
        case 'damage_type':
          comparison = a.damage_type.localeCompare(b.damage_type)
          break
      }
      return filters.sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-adjustr-green mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error Loading Results</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link href="/" className="inline-block bg-adjustr-green text-white py-2 px-6 rounded-lg hover:bg-adjustr-green-dark transition-colors">
            Back to Upload
          </Link>
        </div>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No results found</p>
        </div>
      </div>
    )
  }

  const { video, inferences, total_estimated_cost, damage_summary } = results
  const filteredInferences = getFilteredInferences()
  const availableDamageTypes = Object.keys(damage_summary.damage_counts || {})
  const isVideo = video.filename.toLowerCase().match(/\.(mp4|mov)$/)

  return (
    <>
      <Head>
        <title>Results - {video.filename} | AdjustR</title>
        <meta name="description" content="Damage assessment results" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-6">
            <Link href="/" className="inline-flex items-center text-adjustr-green hover:text-adjustr-green-dark mb-4">
              <svg className="h-5 w-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              New Analysis
            </Link>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Damage Assessment Results</h1>
                <p className="text-gray-600 mt-1">{video.filename}</p>
              </div>
              {/* View Mode Toggle */}
              <div className="flex items-center space-x-2 bg-white rounded-lg shadow p-1">
                <button
                  onClick={() => setViewMode('overview')}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                    viewMode === 'overview'
                      ? 'bg-adjustr-green text-white'
                      : 'text-gray-600 hover:text-adjustr-green'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setViewMode('gallery')}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                    viewMode === 'gallery'
                      ? 'bg-adjustr-green text-white'
                      : 'text-gray-600 hover:text-adjustr-green'
                  }`}
                >
                  Gallery
                </button>
                <button
                  onClick={() => setViewMode('table')}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                    viewMode === 'table'
                      ? 'bg-adjustr-green text-white'
                      : 'text-gray-600 hover:text-adjustr-green'
                  }`}
                >
                  Table
                </button>
                <button
                  onClick={() => setViewMode('charts')}
                  className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                    viewMode === 'charts'
                      ? 'bg-adjustr-green text-white'
                      : 'text-gray-600 hover:text-adjustr-green'
                  }`}
                >
                  Charts
                </button>
              </div>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {/* Total Cost */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Estimated Cost</p>
                  <p className="text-2xl font-bold text-adjustr-green">
                    ${total_estimated_cost.toLocaleString()}
                  </p>
                </div>
                <div className="bg-adjustr-green bg-opacity-10 p-3 rounded-full">
                  <svg className="h-6 w-6 text-adjustr-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Total Damages */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Damages</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {filteredInferences.length}
                    {filteredInferences.length !== inferences.length && (
                      <span className="text-sm text-gray-500 ml-1">/ {inferences.length}</span>
                    )}
                  </p>
                </div>
                <div className="bg-red-50 p-3 rounded-full">
                  <svg className="h-6 w-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Damage Types */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Damage Types</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {damage_summary.unique_damage_types}
                  </p>
                </div>
                <div className="bg-yellow-50 p-3 rounded-full">
                  <svg className="h-6 w-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Avg Confidence */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Avg Confidence</p>
                  <p className="text-2xl font-bold text-gray-800">
                    {(damage_summary.avg_confidence * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-blue-50 p-3 rounded-full">
                  <svg className="h-6 w-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Filter Panel */}
          <div className="mb-6">
            <FilterPanel
              availableDamageTypes={availableDamageTypes}
              onFilterChange={setFilters}
              initialFilters={filters}
            />
          </div>

          {/* Content Based on View Mode */}
          {viewMode === 'overview' && (
            <div className="space-y-6">
              {/* Video Player (if video) */}
              {isVideo && (
                <VideoPlayer
                  videoUrl={video.s3_url}
                  frameCount={video.frame_count || 0}
                  duration={video.duration || 0}
                />
              )}

              {/* Damage Breakdown */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* By Type */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Damage by Type</h2>
                  <div className="space-y-3">
                    {Object.entries(damage_summary.damage_counts || {}).map(([type, data]: [string, any]) => (
                      <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                        <div>
                          <p className="font-medium text-gray-800">{type}</p>
                          <p className="text-sm text-gray-600">
                            {data.count} detected • {(data.avg_confidence * 100).toFixed(0)}% confidence
                          </p>
                        </div>
                        <span className="text-lg font-bold text-adjustr-green">
                          {data.count}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* By Severity */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Damage by Severity</h2>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-red-50 rounded">
                      <div className="flex items-center">
                        <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-3"></span>
                        <span className="font-medium text-gray-800">High Severity</span>
                      </div>
                      <span className="text-lg font-bold text-red-600">
                        {damage_summary.severity_counts.high}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-yellow-50 rounded">
                      <div className="flex items-center">
                        <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-3"></span>
                        <span className="font-medium text-gray-800">Medium Severity</span>
                      </div>
                      <span className="text-lg font-bold text-yellow-600">
                        {damage_summary.severity_counts.medium}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                      <div className="flex items-center">
                        <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-3"></span>
                        <span className="font-medium text-gray-800">Low Severity</span>
                      </div>
                      <span className="text-lg font-bold text-green-600">
                        {damage_summary.severity_counts.low}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {viewMode === 'gallery' && (
            <FrameGallery inferences={filteredInferences} />
          )}

          {viewMode === 'table' && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-800">Detailed Detection Results</h2>
                <p className="text-sm text-gray-600 mt-1">
                  {filteredInferences.length} damage{filteredInferences.length !== 1 ? 's' : ''} detected
                  {filteredInferences.length !== inferences.length && (
                    <span className="text-gray-500"> (filtered from {inferences.length})</span>
                  )}
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Frame
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Damage Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Severity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confidence
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredInferences.map((inference) => (
                      <tr key={inference.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          Frame {inference.frame_number}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {inference.damage_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full
                            ${inference.severity === 'high' ? 'bg-red-100 text-red-800' : ''}
                            ${inference.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : ''}
                            ${inference.severity === 'low' ? 'bg-green-100 text-green-800' : ''}
                          `}>
                            {inference.severity.charAt(0).toUpperCase() + inference.severity.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {(inference.confidence * 100).toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {viewMode === 'charts' && (
            <DamageChart
              damageCounts={damage_summary.damage_counts || {}}
              severityCounts={damage_summary.severity_counts}
            />
          )}

          {/* Actions */}
          <div className="mt-8 flex justify-center gap-4">
            <Link
              href="/"
              className="bg-white border-2 border-adjustr-green text-adjustr-green py-3 px-8 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              New Analysis
            </Link>
            <button
              onClick={() => window.print()}
              className="bg-adjustr-green text-white py-3 px-8 rounded-lg font-semibold hover:bg-adjustr-green-dark transition-colors"
            >
              Print Report
            </button>
          </div>
        </div>
      </main>
    </>
  )
}
