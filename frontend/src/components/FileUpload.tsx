import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

interface FileUploadProps {
  onUploadSuccess: (videoId: number) => void
  onUploadError: (error: string) => void
  disabled?: boolean
}

export default function FileUpload({ onUploadSuccess, onUploadError, disabled = false }: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/mp4': ['.mp4'],
      'video/quicktime': ['.mov'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: false,
    disabled: disabled || uploading
  })

  const handleUpload = async () => {
    if (!selectedFile) {
      onUploadError('Please select a file first')
      return
    }

    setUploading(true)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)
      setProgress(100)

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Upload failed')
      }

      const data = await response.json()

      // Success!
      setTimeout(() => {
        onUploadSuccess(data.video_id)
      }, 500)

    } catch (error: any) {
      console.error('Upload error:', error)
      onUploadError(error.message || 'Failed to upload file')
      setProgress(0)
    } finally {
      setUploading(false)
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setProgress(0)
  }

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer
            ${isDragActive
              ? 'border-adjustr-green bg-adjustr-green bg-opacity-5'
              : 'border-gray-300 hover:border-adjustr-green'
            }`}
        >
          <input {...getInputProps()} />

          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          <p className="mt-4 text-sm text-gray-600">
            {isDragActive ? (
              <span className="font-semibold text-adjustr-green">
                Drop the file here
              </span>
            ) : (
              <>
                <span className="font-semibold text-adjustr-green">
                  Click to upload
                </span>{' '}
                or drag and drop
              </>
            )}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            MP4, MOV, JPG, PNG up to 100MB
          </p>
        </div>
      ) : (
        /* Selected file display */
        <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {selectedFile.type.startsWith('image/') ? (
                  <svg className="h-10 w-10 text-adjustr-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                ) : (
                  <svg className="h-10 w-10 text-adjustr-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                )}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>

            {!uploading && (
              <button
                onClick={handleRemoveFile}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Progress bar */}
          {uploading && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-600">Uploading...</span>
                <span className="text-xs text-gray-600">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-adjustr-green h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Upload button */}
      {selectedFile && !uploading && !disabled && (
        <button
          onClick={handleUpload}
          className="w-full bg-adjustr-green text-white py-3 px-6 rounded-lg font-semibold hover:bg-adjustr-green-dark transition-colors"
        >
          Analyze Damage
        </button>
      )}

      {(uploading || disabled) && selectedFile && (
        <button
          disabled
          className="w-full bg-gray-400 text-white py-3 px-6 rounded-lg font-semibold cursor-not-allowed"
        >
          {uploading ? 'Uploading...' : 'Processing...'}
        </button>
      )}
    </div>
  )
}
