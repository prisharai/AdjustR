import { useState } from 'react'

interface Inference {
  id: number
  frame_number: number
  frame_url: string
  damage_type: string
  severity: string
  confidence: number
  bounding_box?: any
}

interface FrameGalleryProps {
  inferences: Inference[]
  apiBaseUrl?: string
}

export default function FrameGallery({ inferences, apiBaseUrl = 'http://localhost:8000' }: FrameGalleryProps) {
  const [selectedFrame, setSelectedFrame] = useState<number | null>(null)
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set())

  // Group inferences by frame
  const frameGroups = inferences.reduce((acc, inference) => {
    const frameNum = inference.frame_number
    if (!acc[frameNum]) {
      acc[frameNum] = {
        frame_number: frameNum,
        frame_url: inference.frame_url,
        inferences: []
      }
    }
    acc[frameNum].inferences.push(inference)
    return acc
  }, {} as Record<number, { frame_number: number; frame_url: string; inferences: Inference[] }>)

  const frames = Object.values(frameGroups).sort((a, b) => a.frame_number - b.frame_number)

  const handleImageError = (frameNum: number) => {
    setImageErrors(prev => new Set(prev).add(frameNum))
  }

  const downloadFrame = (frameUrl: string, frameNumber: number) => {
    const fullUrl = frameUrl.startsWith('http') ? frameUrl : `${apiBaseUrl}${frameUrl}`
    fetch(fullUrl)
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `frame_${frameNumber}.jpg`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      })
      .catch(err => {
        console.error('Download failed:', err)
        alert('Failed to download frame')
      })
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (frames.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <svg className="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p className="text-gray-600">No frames to display</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Gallery Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {frames.map((frame) => {
          const hasError = imageErrors.has(frame.frame_number)
          const fullImageUrl = frame.frame_url.startsWith('http')
            ? frame.frame_url
            : `${apiBaseUrl}${frame.frame_url}`

          const highestSeverity = frame.inferences.reduce((max, inf) => {
            const severityOrder = { high: 3, medium: 2, low: 1 }
            const currentSeverity = severityOrder[inf.severity.toLowerCase() as keyof typeof severityOrder] || 0
            const maxSeverity = severityOrder[max.toLowerCase() as keyof typeof severityOrder] || 0
            return currentSeverity > maxSeverity ? inf.severity : max
          }, 'low')

          return (
            <div
              key={frame.frame_number}
              className={`bg-white rounded-lg shadow-md overflow-hidden transition-all hover:shadow-lg cursor-pointer ${
                selectedFrame === frame.frame_number ? 'ring-2 ring-adjustr-green' : ''
              }`}
              onClick={() => setSelectedFrame(selectedFrame === frame.frame_number ? null : frame.frame_number)}
            >
              {/* Frame Image */}
              <div className="relative aspect-video bg-gray-100">
                {!hasError ? (
                  <img
                    src={fullImageUrl}
                    alt={`Frame ${frame.frame_number}`}
                    className="w-full h-full object-cover"
                    onError={() => handleImageError(frame.frame_number)}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center">
                      <svg className="h-12 w-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p className="text-sm text-gray-500">Image unavailable</p>
                    </div>
                  </div>
                )}

                {/* Frame Number Badge */}
                <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs font-semibold">
                  Frame {frame.frame_number}
                </div>

                {/* Damage Count Badge */}
                <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs font-semibold">
                  {frame.inferences.length} {frame.inferences.length === 1 ? 'damage' : 'damages'}
                </div>

                {/* Highest Severity Badge */}
                <div className={`absolute bottom-2 right-2 px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(highestSeverity)}`}>
                  {highestSeverity.charAt(0).toUpperCase() + highestSeverity.slice(1)}
                </div>
              </div>

              {/* Frame Info */}
              <div className="p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    {frame.inferences.length} Detection{frame.inferences.length !== 1 ? 's' : ''}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      downloadFrame(frame.frame_url, frame.frame_number)
                    }}
                    className="text-adjustr-green hover:text-adjustr-green-dark"
                    title="Download frame"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                  </button>
                </div>

                {/* Damage Types */}
                <div className="flex flex-wrap gap-1">
                  {Array.from(new Set(frame.inferences.map(inf => inf.damage_type))).map(type => (
                    <span
                      key={type}
                      className="inline-block px-2 py-1 text-xs font-medium bg-adjustr-green bg-opacity-10 text-adjustr-green rounded"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              </div>

              {/* Expanded Details */}
              {selectedFrame === frame.frame_number && (
                <div className="border-t border-gray-200 p-3 bg-gray-50">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Detections:</h4>
                  <div className="space-y-2">
                    {frame.inferences.map((inference) => (
                      <div key={inference.id} className="text-xs bg-white p-2 rounded border border-gray-200">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-gray-800">{inference.damage_type}</span>
                          <span className={`px-2 py-0.5 rounded font-semibold ${getSeverityColor(inference.severity)}`}>
                            {inference.severity}
                          </span>
                        </div>
                        <div className="text-gray-600">
                          Confidence: <span className="font-medium">{(inference.confidence * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Frame Gallery</p>
            <p>
              Showing {frames.length} frame{frames.length !== 1 ? 's' : ''} with {inferences.length} total detection{inferences.length !== 1 ? 's' : ''}.
              Click on a frame to see detailed detection information.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
