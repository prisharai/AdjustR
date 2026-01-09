import { useRef, useState, useEffect } from 'react'

interface VideoPlayerProps {
  videoUrl: string
  frameCount?: number
  duration?: number
  apiBaseUrl?: string
  onTimeUpdate?: (currentTime: number, frameNumber: number) => void
}

export default function VideoPlayer({
  videoUrl,
  frameCount = 0,
  duration = 0,
  apiBaseUrl = 'http://localhost:8000',
  onTimeUpdate
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [currentFrame, setCurrentFrame] = useState(0)
  const [videoError, setVideoError] = useState(false)

  const fullVideoUrl = videoUrl.startsWith('http') ? videoUrl : `${apiBaseUrl}${videoUrl}`

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => {
      const time = video.currentTime
      setCurrentTime(time)

      // Calculate approximate frame number based on time
      // Assuming frames are extracted every 2 seconds
      const estimatedFrame = Math.floor(time / 2)
      setCurrentFrame(estimatedFrame)

      if (onTimeUpdate) {
        onTimeUpdate(time, estimatedFrame)
      }
    }

    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)
    video.addEventListener('ended', handleEnded)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('pause', handlePause)
      video.removeEventListener('ended', handleEnded)
    }
  }, [onTimeUpdate])

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return

    if (isPlaying) {
      video.pause()
    } else {
      video.play()
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current
    if (!video) return

    const time = parseFloat(e.target.value)
    video.currentTime = time
    setCurrentTime(time)
  }

  const skipToFrame = (frameNumber: number) => {
    const video = videoRef.current
    if (!video) return

    // Assuming frames are extracted every 2 seconds
    const time = frameNumber * 2
    video.currentTime = Math.min(time, video.duration)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (videoError) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center">
          <svg className="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-600 mb-2">Video unavailable</p>
          <p className="text-sm text-gray-500">The video file could not be loaded</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Video Container */}
      <div className="relative bg-black aspect-video">
        <video
          ref={videoRef}
          src={fullVideoUrl}
          className="w-full h-full"
          onError={() => setVideoError(true)}
        >
          Your browser does not support the video tag.
        </video>

        {/* Play/Pause Overlay */}
        <div
          className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 hover:bg-opacity-30 transition-all cursor-pointer"
          onClick={togglePlay}
        >
          {!isPlaying && (
            <div className="bg-adjustr-green bg-opacity-90 rounded-full p-4 hover:bg-opacity-100 transition-all">
              <svg className="h-12 w-12 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
              </svg>
            </div>
          )}
        </div>

        {/* Current Frame Indicator */}
        <div className="absolute top-4 left-4 bg-black bg-opacity-75 text-white px-3 py-1 rounded text-sm font-semibold">
          Frame ~{currentFrame}
        </div>
      </div>

      {/* Controls */}
      <div className="p-4 bg-gray-50">
        {/* Progress Bar */}
        <div className="mb-3">
          <input
            type="range"
            min="0"
            max={duration || videoRef.current?.duration || 0}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-adjustr-green"
          />
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration || videoRef.current?.duration || 0)}</span>
          </div>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={togglePlay}
              className="p-2 bg-adjustr-green text-white rounded hover:bg-adjustr-green-dark transition-colors"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? (
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
              )}
            </button>

            <button
              onClick={() => skipToFrame(Math.max(0, currentFrame - 1))}
              className="p-2 text-gray-600 hover:text-adjustr-green transition-colors"
              title="Previous frame"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <button
              onClick={() => skipToFrame(Math.min(frameCount - 1, currentFrame + 1))}
              className="p-2 text-gray-600 hover:text-adjustr-green transition-colors"
              title="Next frame"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="text-sm text-gray-600">
            Frame {currentFrame} of {frameCount}
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <div className="flex items-start">
          <svg className="h-5 w-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div className="text-sm text-gray-600">
            <p className="font-medium mb-1">Video Playback</p>
            <p>
              Scrub through the video to see damage detections at different points.
              Frames are extracted approximately every 2 seconds.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
