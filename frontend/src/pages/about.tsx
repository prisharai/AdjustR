import React from 'react'
import NavHeader from '../components/NavHeader'
import Breadcrumbs from '../components/Breadcrumbs'

const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumbs items={[{ label: 'About' }]} />

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <svg
                className="w-8 h-8 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              About AdjustR
            </h1>
            <p className="text-gray-600">
              AI-Powered Property Damage Assessment for Insurance Adjusters
            </p>
          </div>

          {/* Description */}
          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">
                What is AdjustR?
              </h2>
              <p>
                AdjustR is an advanced damage assessment tool that uses artificial
                intelligence to analyze property damage from videos and images.
                Built specifically for insurance adjusters, AdjustR streamlines the
                assessment process, providing fast and accurate damage detection
                and cost estimation.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">
                Key Features
              </h2>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <svg
                    className="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span>
                    <strong>AI-Powered Detection:</strong> Automatically identify
                    damage types including water damage, mold, cracks, and more
                  </span>
                </li>
                <li className="flex items-start">
                  <svg
                    className="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span>
                    <strong>Video & Image Support:</strong> Process both videos
                    and static images for comprehensive assessments
                  </span>
                </li>
                <li className="flex items-start">
                  <svg
                    className="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span>
                    <strong>Cost Estimation:</strong> Get instant cost estimates
                    for detected damage
                  </span>
                </li>
                <li className="flex items-start">
                  <svg
                    className="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span>
                    <strong>Interactive Dashboard:</strong> Explore results with
                    multiple views, filtering, and visualization options
                  </span>
                </li>
                <li className="flex items-start">
                  <svg
                    className="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span>
                    <strong>Assessment History:</strong> Keep track of all your
                    previous assessments in one place
                  </span>
                </li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">
                How It Works
              </h2>
              <ol className="space-y-3">
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">
                    1
                  </span>
                  <span>
                    <strong>Upload:</strong> Upload a video or image of the
                    property damage
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">
                    2
                  </span>
                  <span>
                    <strong>Process:</strong> Our AI analyzes the content and
                    extracts keyframes from videos
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">
                    3
                  </span>
                  <span>
                    <strong>Detect:</strong> YOLOv8 AI model identifies and
                    classifies damage with confidence scores
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">
                    4
                  </span>
                  <span>
                    <strong>Review:</strong> Explore results in an interactive
                    dashboard with multiple views
                  </span>
                </li>
              </ol>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">
                Technology Stack
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Backend</h3>
                  <ul className="text-sm space-y-1 text-gray-600">
                    <li>FastAPI</li>
                    <li>Python 3.11</li>
                    <li>PostgreSQL</li>
                    <li>YOLOv8 (Ultralytics)</li>
                    <li>OpenCV</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Frontend</h3>
                  <ul className="text-sm space-y-1 text-gray-600">
                    <li>Next.js 14</li>
                    <li>React 18</li>
                    <li>TypeScript</li>
                    <li>TailwindCSS</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="border-t border-gray-200 pt-6">
              <p className="text-sm text-gray-600">
                <strong>Version:</strong> 1.0.0 (MVP)
                <br />
                <strong>Last Updated:</strong> January 2026
                <br />
                <strong>Status:</strong> Beta Release
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AboutPage
