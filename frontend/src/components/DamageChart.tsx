interface DamageChartProps {
  damageCounts: Record<string, {
    count: number
    avg_confidence: number
    severities: {
      low: number
      medium: number
      high: number
    }
  }>
  severityCounts: {
    low: number
    medium: number
    high: number
  }
}

export default function DamageChart({ damageCounts, severityCounts }: DamageChartProps) {
  const damageTypes = Object.entries(damageCounts)
  const maxCount = Math.max(...damageTypes.map(([_, data]) => data.count), 1)

  const totalSeverity = severityCounts.low + severityCounts.medium + severityCounts.high
  const severityData = [
    { label: 'High', count: severityCounts.high, color: 'bg-red-500', percentage: (severityCounts.high / totalSeverity) * 100 },
    { label: 'Medium', count: severityCounts.medium, color: 'bg-yellow-500', percentage: (severityCounts.medium / totalSeverity) * 100 },
    { label: 'Low', count: severityCounts.low, color: 'bg-green-500', percentage: (severityCounts.low / totalSeverity) * 100 },
  ]

  return (
    <div className="space-y-6">
      {/* Damage Type Bar Chart */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Damage Distribution</h3>
          <svg className="h-5 w-5 text-adjustr-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>

        <div className="space-y-4">
          {damageTypes.map(([type, data]) => (
            <div key={type}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">{type}</span>
                <div className="text-sm text-gray-600">
                  <span className="font-semibold text-adjustr-green">{data.count}</span>
                  <span className="mx-1">•</span>
                  <span>{(data.avg_confidence * 100).toFixed(0)}% confidence</span>
                </div>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-adjustr-green to-green-400 rounded-full transition-all duration-500 ease-out flex items-center justify-end pr-2"
                  style={{ width: `${(data.count / maxCount) * 100}%` }}
                >
                  {(data.count / maxCount) > 0.15 && (
                    <span className="text-xs font-semibold text-white">{data.count}</span>
                  )}
                </div>
              </div>
              {/* Severity breakdown for this damage type */}
              <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                {data.severities.high > 0 && (
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-red-500 rounded-full mr-1"></span>
                    {data.severities.high} high
                  </span>
                )}
                {data.severities.medium > 0 && (
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></span>
                    {data.severities.medium} medium
                  </span>
                )}
                {data.severities.low > 0 && (
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                    {data.severities.low} low
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Severity Distribution */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Severity Distribution</h3>
          <svg className="h-5 w-5 text-adjustr-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
        </div>

        {/* Stacked Bar */}
        <div className="mb-4">
          <div className="flex h-12 rounded-lg overflow-hidden">
            {severityData.map((severity, index) => (
              severity.count > 0 && (
                <div
                  key={severity.label}
                  className={`${severity.color} flex items-center justify-center text-white text-sm font-semibold transition-all duration-500 ease-out hover:opacity-90`}
                  style={{ width: `${severity.percentage}%` }}
                  title={`${severity.label}: ${severity.count} (${severity.percentage.toFixed(1)}%)`}
                >
                  {severity.percentage > 10 && (
                    <span>{severity.count}</span>
                  )}
                </div>
              )
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="grid grid-cols-3 gap-4">
          {severityData.map((severity) => (
            <div key={severity.label} className="text-center">
              <div className={`h-2 ${severity.color} rounded-full mb-2`}></div>
              <div className="text-lg font-bold text-gray-800">{severity.count}</div>
              <div className="text-xs text-gray-600">{severity.label} Severity</div>
              <div className="text-xs text-gray-500">{severity.percentage.toFixed(1)}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Confidence Distribution */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Confidence Levels</h3>
          <svg className="h-5 w-5 text-adjustr-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {damageTypes.map(([type, data]) => (
            <div key={type} className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-sm font-medium text-gray-700 mb-2 truncate" title={type}>
                {type}
              </div>
              <div className="relative">
                <svg className="w-full h-20" viewBox="0 0 100 100">
                  {/* Background circle */}
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="12"
                  />
                  {/* Progress circle */}
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="12"
                    strokeDasharray={`${data.avg_confidence * 251.2} 251.2`}
                    strokeLinecap="round"
                    transform="rotate(-90 50 50)"
                    className="transition-all duration-500"
                  />
                  <text
                    x="50"
                    y="50"
                    textAnchor="middle"
                    dy=".3em"
                    className="text-xl font-bold fill-gray-800"
                  >
                    {(data.avg_confidence * 100).toFixed(0)}%
                  </text>
                </svg>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Avg confidence
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="bg-gradient-to-r from-adjustr-green to-green-400 rounded-lg shadow-md p-6 text-white">
        <div className="flex items-center mb-3">
          <svg className="h-6 w-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          <h3 className="text-lg font-semibold">Key Insights</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-2xl font-bold">{damageTypes.length}</div>
            <div className="text-sm opacity-90">Damage Types Found</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{totalSeverity}</div>
            <div className="text-sm opacity-90">Total Detections</div>
          </div>
          <div>
            <div className="text-2xl font-bold">
              {severityCounts.high > 0 ? severityCounts.high : '-'}
            </div>
            <div className="text-sm opacity-90">Critical Issues</div>
          </div>
          <div>
            <div className="text-2xl font-bold">
              {damageTypes.length > 0
                ? (damageTypes.reduce((sum, [_, data]) => sum + data.avg_confidence, 0) / damageTypes.length * 100).toFixed(0) + '%'
                : '-'}
            </div>
            <div className="text-sm opacity-90">Overall Confidence</div>
          </div>
        </div>
      </div>
    </div>
  )
}
