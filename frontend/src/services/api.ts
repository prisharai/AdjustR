import axios, { AxiosProgressEvent } from 'axios';

// Configure axios base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Type definitions
export interface UploadResponse {
  video_id: number;
  filename: string;
  s3_url: string;
  status: string;
  message: string;
}

export interface UploadStatus {
  video_id: number;
  status: string;
  filename: string;
  frame_count?: number;
  message?: string;
}

export interface AnalysisStatus {
  video_id: number;
  status: string;
  total_inferences: number;
  total_estimated_cost: number;
  damage_counts: Record<string, number>;
  severity_counts: {
    low: number;
    medium: number;
    high: number;
  };
  frame_count: number;
  analysis_complete: boolean;
}

export interface ResultsResponse {
  video: {
    id: number;
    filename: string;
    status: string;
    upload_timestamp: string;
    frame_count: number;
  };
  inferences: Array<{
    id: number;
    frame_number: number;
    damage_type: string;
    severity: string;
    confidence: number;
    bounding_box?: any;
  }>;
  total_estimated_cost: number;
  damage_summary: any;
}

// Upload video/image with progress tracking
export const uploadVideo = async (
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
      if (progressEvent.total && onProgress) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    },
  });

  return response.data;
};

// Check upload status
export const checkUploadStatus = async (videoId: number): Promise<UploadStatus> => {
  const response = await api.get(`/api/upload/status/${videoId}`);
  return response.data;
};

// Analyze video
export const analyzeVideo = async (videoId: number) => {
  const response = await api.post(`/api/analyze/${videoId}`);
  return response.data;
};

// Check analysis status
export const checkAnalysisStatus = async (videoId: number): Promise<AnalysisStatus> => {
  const response = await api.get(`/api/analyze/status/${videoId}`);
  return response.data;
};

// Get results
export const getResults = async (
  videoId: number,
  filters?: {
    damage_type?: string;
    severity?: string;
    min_confidence?: number;
    sort_by?: string;
    sort_order?: string;
  }
): Promise<ResultsResponse> => {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value));
      }
    });
  }

  const response = await api.get(`/api/results/${videoId}?${params.toString()}`);
  return response.data;
};

// List all videos
export interface VideoListItem {
  video_id: number;
  filename: string;
  status: string;
  upload_timestamp: string;
  file_size: number;
  duration?: number;
  frame_count: number;
  inference_count: number;
}

export interface VideoListResponse {
  videos: VideoListItem[];
  total: number;
  limit: number;
  offset: number;
}

export const listVideos = async (limit = 50, offset = 0): Promise<VideoListResponse> => {
  const response = await api.get(`/api/videos?limit=${limit}&offset=${offset}`);
  return response.data;
};

// Delete video
export const deleteVideo = async (videoId: number) => {
  const response = await api.delete(`/api/upload/${videoId}`);
  return response.data;
};

// Delete analysis
export const deleteAnalysis = async (videoId: number) => {
  const response = await api.delete(`/api/analyze/${videoId}`);
  return response.data;
};

// Generate report
export const generateReport = async (videoId: number) => {
  const response = await api.post(`/api/report/${videoId}`);
  return response.data;
};

// Download report
export const downloadReport = (videoId: number) => {
  window.open(`${API_BASE_URL}/api/report/${videoId}/download`, '_blank');
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Helper function to poll status until complete
export const pollUntilComplete = async (
  checkFn: () => Promise<any>,
  isCompleteFn: (data: any) => boolean,
  maxAttempts = 60,
  intervalMs = 2000
): Promise<any> => {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const data = await checkFn();

    if (isCompleteFn(data)) {
      return data;
    }

    if (data.status === 'error') {
      throw new Error('Processing failed with error status');
    }

    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }

  throw new Error('Polling timeout: operation did not complete in time');
};

export default api;
