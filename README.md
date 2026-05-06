# NextLeap RAG Chatbot 🚀

A professional, end-to-end RAG (Retrieval-Augmented Generation) chatbot designed specifically for NextLeap courses and fellowships. This system features automated data acquisition, a semantic knowledge base, and a high-speed streaming UI.

## ✨ Features

*   **Automated Data Scraping**: Custom Playwright-based scraper for 5 major NextLeap cohorts (PM, UX, Data, Business, GenAI).
*   **High-Speed RAG Engine**: Powered by **Groq (Llama 3.1 8B)** with real-time streaming for instant responses.
*   **Intelligent Retrieval**: Lightweight, memory-efficient search engine with synonym mapping (Fellowship = Course).
*   **Modern Dashboard**: Glassmorphic dark-mode UI with chat history and course suggestions.
*   **Autonomous Maintenance**: Daily automated updates via **GitHub Actions** at 10 AM IST.
*   **Production Ready**: Configured for instant deployment on **Vercel**.

## 🛠️ Architecture

The project is built in 6 modular phases:
1.  **Data Acquisition**: Web scraping and metadata extraction.
2.  **Knowledge Base**: Semantic chunking and lightweight search indexing.
3.  **RAG Core**: Integration with Groq LLM and strict context-bound prompts.
4.  **Backend API**: FastAPI with support for Server-Sent Events (SSE) streaming.
5.  **Frontend UI**: Modern, responsive dashboard.
6.  **Automated Scheduler**: Daily CI/CD pipeline for data freshness.

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Groq API Key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/suvadeepd8work-source/Rag-Chatbot-1.git
   cd Rag-Chatbot-1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Configure environment:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running Locally

1. Start the backend and frontend:
   ```bash
   python Phase_4_Backend_API/main.py
   ```
2. Open your browser and navigate to:
   `http://localhost:8000/gui`

## ☁️ Deployment

### Vercel
1. Import the repository into Vercel.
2. Add `GROQ_API_KEY` to the environment variables.
3. Your app will be live at `https://your-app.vercel.app/gui`.

### GitHub Actions (Auto-Update)
1. Add `GROQ_API_KEY` to your GitHub Repository Secrets.
2. The bot will automatically update its knowledge base every day at 10 AM IST.

## 📄 License
MIT License
