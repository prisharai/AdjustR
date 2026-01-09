import { useState, useEffect } from 'react'

export interface FilterOptions {
  damageTypes: string[]
  severities: ('low' | 'medium' | 'high')[]
  minConfidence: number
  sortBy: 'frame_number' | 'confidence' | 'severity' | 'damage_type'
  sortOrder: 'asc' | 'desc'
}

interface FilterPanelProps {
  availableDamageTypes: string[]
  onFilterChange: (filters: FilterOptions) => void
  initialFilters?: Partial<FilterOptions>
}

export default function FilterPanel({
  availableDamageTypes,
  onFilterChange,
  initialFilters = {}
}: FilterPanelProps) {
  const [damageTypes, setDamageTypes] = useState<string[]>(initialFilters.damageTypes || [])
  const [severities, setSeverities] = useState<('low' | 'medium' | 'high')[]>(initialFilters.severities || [])
  const [minConfidence, setMinConfidence] = useState<number>(initialFilters.minConfidence || 0)
  const [sortBy, setSortBy] = useState<FilterOptions['sortBy']>(initialFilters.sortBy || 'frame_number')
  const [sortOrder, setSortOrder] = useState<FilterOptions['sortOrder']>(initialFilters.sortOrder || 'asc')
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    onFilterChange({
      damageTypes,
      severities,
      minConfidence,
      sortBy,
      sortOrder
    })
  }, [damageTypes, severities, minConfidence, sortBy, sortOrder])

  const toggleDamageType = (type: string) => {
    setDamageTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    )
  }

  const toggleSeverity = (severity: 'low' | 'medium' | 'high') => {
    setSeverities(prev =>
      prev.includes(severity)
        ? prev.filter(s => s !== severity)
        : [...prev, severity]
    )
  }

  const resetFilters = () => {
    setDamageTypes([])
    setSeverities([])
    setMinConfidence(0)
    setSortBy('frame_number')
    setSortOrder('asc')
  }

  const activeFilterCount = damageTypes.length + severities.length + (minConfidence > 0 ? 1 : 0)

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div
        className="p-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2">
          <svg className="h-5 w-5 text-adjustr-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-800">Filters & Sorting</h3>
          {activeFilterCount > 0 && (
            <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-adjustr-green rounded-full">
              {activeFilterCount}
            </span>
          )}
        </div>
        <svg
          className={`h-5 w-5 text-gray-500 transition-transform ${isExpanded ? 'transform rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* Filters Content */}
      {isExpanded && (
        <div className="p-4 space-y-6">
          {/* Damage Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Damage Type
            </label>
            <div className="space-y-2">
              {availableDamageTypes.map(type => (
                <label key={type} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={damageTypes.includes(type)}
                    onChange={() => toggleDamageType(type)}
                    className="w-4 h-4 text-adjustr-green border-gray-300 rounded focus:ring-adjustr-green"
                  />
                  <span className="text-sm text-gray-700">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Severity Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Severity Level
            </label>
            <div className="space-y-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={severities.includes('high')}
                  onChange={() => toggleSeverity('high')}
                  className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                />
                <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                  High
                </span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={severities.includes('medium')}
                  onChange={() => toggleSeverity('medium')}
                  className="w-4 h-4 text-yellow-600 border-gray-300 rounded focus:ring-yellow-500"
                />
                <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
                  Medium
                </span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={severities.includes('low')}
                  onChange={() => toggleSeverity('low')}
                  className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                />
                <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                  Low
                </span>
              </label>
            </div>
          </div>

          {/* Confidence Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Confidence: {minConfidence}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-adjustr-green"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Sorting */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sort By
            </label>
            <div className="grid grid-cols-2 gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as FilterOptions['sortBy'])}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-adjustr-green focus:border-adjustr-green text-sm"
              >
                <option value="frame_number">Frame Number</option>
                <option value="confidence">Confidence</option>
                <option value="severity">Severity</option>
                <option value="damage_type">Damage Type</option>
              </select>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value as FilterOptions['sortOrder'])}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-adjustr-green focus:border-adjustr-green text-sm"
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
          </div>

          {/* Reset Button */}
          {activeFilterCount > 0 && (
            <button
              onClick={resetFilters}
              className="w-full py-2 px-4 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-adjustr-green"
            >
              Reset All Filters
            </button>
          )}
        </div>
      )}
    </div>
  )
}
