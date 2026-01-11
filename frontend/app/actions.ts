"use server";

import { API_ENDPOINTS } from "@/lib/config";

export interface ProcessResult {
    simplifiedText: string;
    imagePrompt: string;
    image: string;
}

export interface Chapter {
    chapter_number: number;
    title: string;
    raw_text: string;
    simplified_text: string;
    image: string;
    image_prompt: string;
    simplified: boolean;
}

export interface ProcessedBook {
    title: string;
    total_chapters: number;
    chapters: Chapter[];
}

export async function processPDF(formData: FormData): Promise<ProcessedBook> {
    try {
        const response = await fetch(API_ENDPOINTS.PROCESS_PDF, {
            method: "POST",
            body: formData,
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        return data;
    } catch (error) {
        console.error("Process PDF Error:", error);
        throw error;
    }
}

export async function simplifyChapter(chapterNumber: number, rawText: string) {
    try {
        const response = await fetch(API_ENDPOINTS.SIMPLIFY_CHAPTER, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                chapter_number: chapterNumber,
                raw_text: rawText,
            }),
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Simplify Chapter Error:", error);
        throw error;
    }
}

export async function generateChapterImages(chapterNumber: number, imagePrompt: string) {
    try {
        const response = await fetch(API_ENDPOINTS.GENERATE_IMAGES, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                chapter_number: chapterNumber,
                image_prompt: imagePrompt,
            }),
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Generate Images Error:", error);
        throw error;
    }
}

export async function sendChatMessage(message: string, bookContext: string, bookTitle: string) {
    try {
        const response = await fetch(API_ENDPOINTS.CHAT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: message,
                book_context: bookContext,
                book_title: bookTitle,
            }),
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Chat Error:", error);
        throw error;
    }
}

