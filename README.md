# 📚 NovelAI

### Team: Finetuners
> **Transforming complex novels into beautifully illustrated children's storybooks with the power of AI.**

[![Live Demo](https://img.shields.io/badge/demo-live-green.svg?style=for-the-badge)](https://novel-ai-one.vercel.app/)
[![Tech Stack](https://img.shields.io/badge/tech-next.js%20|%20fastapi-blue.svg?style=for-the-badge)](https://github.com/GDGoC-GalgotiasUniversity/techsprint-2026-team-finetuners)

---

## 🎯 Project Overview

NovelAI is an innovative platform designed to bridge the gap between complex literature and young readers. By leveraging advanced AI models, we transform standard PDF novels into simplified, engaging, and fully illustrated storybooks tailored for children aged 6 to 8.

### 👥 Team Finetuners
This project was developed during **TechSprint Hackathon 2026**, organized by **GDG on Campus Galgotias University**.

---

## � The Solution

Many classic stories and novels are too complex for young children to enjoy on their own. **NovelAI** solves this by:
1.  **Simplifying Content:** Using Gemini 2.5 Flash to rewrite chapters into child-friendly language.
2.  **Visual Storytelling:** Generating vibrant, context-aware illustrations for every page.
3.  **Interactive Engagement:** Providing a chat interface where kids can ask questions about the story.

---

## ✨ Key Features

- [x] **PDF to Storybook:** Upload any PDF and watch it transform into a children's book.
- [x] **AI Simplification:** Complex sentences are turned into short, easy-to-read sentences perfect for bedtime stories.
- [x] **Dynamic Illustrations:** Contextual image generation using Gemini's image modalities.
- [x] **Interactive Reader:** A modern, responsive UI designed for a seamless reading experience.
- [x] **AI Book Chat:** Ask the AI questions about characters, plot, or specific chapters.
- [x] **Live Progress:** Real-time streaming of the transformation process.

---

## 🛠 Tech Stack

| Category | Technologies Used |
| :--- | :--- |
| **Frontend** | Next.js 16 (App Router), React 19, Tailwind CSS 4, Framer Motion |
| **Backend** | FastAPI (Python 3.11+), Uvicorn |
| **AI Models** | Google Gemini 2.5 Flash (Text), Gemini 2.5 Flash Image |
| **Deployment** | Vercel (Frontend), Dockerized Backend |
| **Libraries** | Lucide React, PyPDF2, GenAI SDK |

---

## � Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the server:
   ```bash
   python main.py
   ```

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

---

## 🔗 Links & Demo
- **🌐 Live Site:** [https://novel-ai-one.vercel.app/](https://novel-ai-one.vercel.app/)
- **📂 GitHub Repo:** [Team Finetuners Repo](https://github.com/GDGoC-GalgotiasUniversity/techsprint-2026-team-finetuners)

---

### 🏆 Acknowledgements
This project was developed during **TechSprint Hackathon 2026**, organized by **GDG on Campus Galgotias University**.
