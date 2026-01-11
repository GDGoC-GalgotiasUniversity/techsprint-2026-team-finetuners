
export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// API 
export const API_ENDPOINTS = {
    PROCESS_PDF: `${BACKEND_URL}/process_pdf`,
    SIMPLIFY_CHAPTER: `${BACKEND_URL}/simplify_chapter`,
    GENERATE_IMAGES: `${BACKEND_URL}/generate_images`,
    CHAT: `${BACKEND_URL}/chat`,
} as const;


if (!process.env.NEXT_PUBLIC_BACKEND_URL && process.env.NODE_ENV === 'production') {
    console.warn('Warning: NEXT_PUBLIC_BACKEND_URL is not set. Using default localhost URL.');
}
