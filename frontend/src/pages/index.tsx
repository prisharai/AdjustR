import Head from 'next/head'
import { useState } from 'react'
import { useRouter } from 'next/router'
import FileUpload from '@/components/FileUpload'
import { analyzeVideo, pollUntilComplete, checkAnalysisStatus } from '@/services/api'

export default function Home() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [statusMessage, setStatusMessage] = useState<string>('')
  const [isProcessing, setIsProcessing] = useState(false)

  const handleUploadSuccess = async (videoId: number) => {
    try {
      setSuccess('Upload successful! Starting analysis...')
      setError(null)
      setIsProcessing(true)
      setStatusMessage('Processing video and extracting frames...')

      // Trigger analysis
      await analyzeVideo(videoId)
      setStatusMessage('Analyzing damage with AI...')

      // Poll for analysis completion
      await pollUntilComplete(
        () => checkAnalysisStatus(videoId),
        (status) => status.analysis_complete === true,
        60, // max attempts
        2000 // 2 second intervals
      )

      setStatusMessage('Analysis complete! Redirecting to results...')

      // Navigate to results page
      setTimeout(() => {
        router.push(`/results/${videoId}`)
      }, 1000)
    } catch (error: any) {
      console.error('Analysis error:', error)
      setError(error.message || 'Analysis failed. Please try again.')
      setIsProcessing(false)
      setStatusMessage('')
    }
  }

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage)
    setSuccess(null)
    setIsProcessing(false)
    setStatusMessage('')
  }

  return (
    <>
      <Head>
        <title>AdjustR - Turn Photos into Instant Damage Insights</title>
        <meta name="description" content="AI-Powered Property Damage Assessment Tool" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <header className="text-center mb-12">
            <h1 className="text-4xl font-bold text-adjustr-green mb-2">
              AdjustR
            </h1>
            <p className="text-gray-600 text-lg">
              Turn photos into instant damage insights
            </p>
          </header>

          {/* Upload Section */}
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Upload Damage Photos or Videos
              </h2>
              <p className="text-gray-600 mb-6">
                Upload property damage photos or videos to receive an instant AI-powered assessment
              </p>

              {/* Error message */}
              {error && (
                <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  <div className="flex items-center">
                    <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span>{error}</span>
                  </div>
                </div>
              )}

              {/* Success message */}
              {success && (
                <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                  <div className="flex items-center">
                    <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>{success}</span>
                  </div>
                </div>
              )}

              {/* Processing status */}
              {isProcessing && statusMessage && (
                <div className="mb-6 bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">
                  <div className="flex items-center">
                    <svg className="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>{statusMessage}</span>
                  </div>
                </div>
              )}

              {/* File Upload Component */}
              <FileUpload
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
                disabled={isProcessing}
              />
            </div>

            {/* Info Section */}
            <div className="mt-8 bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                How it works
              </h3>
              <ol className="space-y-2 text-gray-600">
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-adjustr-green text-white rounded-full flex items-center justify-center text-sm mr-3">
                    1
                  </span>
                  <span>Upload photos or videos of property damage</span>
                </li>
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-adjustr-green text-white rounded-full flex items-center justify-center text-sm mr-3">
                    2
                  </span>
                  <span>Our AI analyzes and detects damage types</span>
                </li>
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-adjustr-green text-white rounded-full flex items-center justify-center text-sm mr-3">
                    3
                  </span>
                  <span>Receive detailed assessment with cost estimates</span>
                </li>
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-adjustr-green text-white rounded-full flex items-center justify-center text-sm mr-3">
                    4
                  </span>
                  <span>Download professional PDF report</span>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
