"use client";

import { useState, useRef } from "react";
import PDFUpload from "@/components/PDFUpload";
import BookDisplay from "@/components/BookDisplay";
import { ProcessedBook } from "@/app/actions";
import { BookOpen } from "lucide-react";
import { API_ENDPOINTS } from "@/lib/config";

export default function Home() {
  const [book, setBook] = useState<ProcessedBook | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");
  const bookDisplayRef = useRef<HTMLDivElement>(null);

  const handleUpload = async (file: File) => {
    setIsProcessing(true);
    setError("");
    setProgress(0);
    setProgressMessage("Starting...");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(API_ENDPOINTS.PROCESS_PDF, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6));

            if (data.type === "progress") {
              setProgress(data.progress);
              setProgressMessage(data.message);
            } else if (data.type === "complete") {
              setBook(data.data);
              setProgress(100);
              setProgressMessage("Complete!");
              setTimeout(() => {
                bookDisplayRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
              }, 100);
            } else if (data.type === "error") {
              throw new Error(data.message);
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
      setError("Something went wrong! Please try again.");
    } finally {
      setIsProcessing(false);
      setProgress(0);
      setProgressMessage("");
    }
  };

  const handleReset = () => {
    setBook(null);
    setError("");
    setProgress(0);
    setProgressMessage("");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-[family-name:var(--font-geist-sans)] p-4 sm:p-8">
      <main className="max-w-6xl mx-auto flex flex-col items-center gap-12 pt-8">

        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-block p-3 bg-white rounded-full shadow-sm mb-2">
            <BookOpen className="w-8 h-8 text-slate-700" />
          </div>
          <h1 className="text-4xl font-bold text-slate-800 tracking-tight">
            NovelAI
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Transform novels into illustrated children's books
          </p>
        </div>

        {error && (
          <div className="w-full max-w-lg bg-red-50 text-red-600 p-4 rounded-xl border border-red-200 text-center">
            {error}
          </div>
        )}

        {isProcessing && (
          <div className="w-full max-w-3xl bg-white rounded-2xl shadow-lg p-6 border border-slate-200">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-slate-700">{progressMessage}</span>
                <span className="text-sm font-semibold text-slate-800">{progress}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-slate-800 h-full rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={bookDisplayRef} className="w-full transition-all duration-500">
          {!book ? (
            <PDFUpload onUpload={handleUpload} isProcessing={isProcessing} />
          ) : (
            <BookDisplay book={book} onReset={handleReset} />
          )}
        </div>

      </main>

      <footer className="mt-20 text-center text-slate-400 text-sm pb-8">
        Powered by NovelAI
      </footer>
    </div>
  );
}

