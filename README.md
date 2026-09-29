# Website Cloning Agent

An automated, full-stack AI agent capable of analyzing live websites, extracting core layouts, design tokens, and components, and regenerating them as responsive **Next.js 14+ App Router** projects styled with **Tailwind CSS**. 

Built with a Streamlit interface, the framework features an automated TypeScript compilation self-healing system and high-availability Gemini API wrapper structures.

---

## Features

* **Visual & Structural Analysis:** Captures live desktop/mobile viewport snapshots alongside DOM trees via Playwright to generate structural component specifications.
* **Zero-Config Component Synthesis:** Generates isolated, reusable TypeScript components mapping exactly to the input brand token guidelines without writing template configurations.
* **Self-Healing Build System:** Pipelines runtime build checks (`npx tsc --noEmit`) directly back to the model array to automatically fix syntax constraints over a multi-pass loop.
* **Resilient Multi-Model Routing:** Transparently catches server spikes using automated exponential backoff intervals and shifts workloads across fallback layers (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`).
* **Side-by-Side Playground:** Interactive wide-layout UI separating sandbox code updates from device-responsive `iframe` previews.

---

## Tech Stack

* **Orchestration & UI:** Streamlit, Python Dotenv
* **AI Engine:** Google GenAI SDK (`gemini-2.5-flash`)
* **Scraping Engine:** Playwright (Chromium Headless automation)
* **Target Layout Framework:** Next.js 14 (App Router), TypeScript, Tailwind CSS, npm

---

## Local Installation & Architecture

### Prerequisites
* Python 3.10+
* Node.js 20+
* Google Gemini API Key

### Configuration Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com
   cd website-cloning-agent
   ```

2. **Initialize Python Environment:**
   ```bash
   python -m venv venv
   # Windows Activation:
   venv\Scripts\activate
   # macOS/Linux Activation:
   # source venv/bin/activate
   
   pip install google-genai playwright streamlit python-dotenv
   playwright install chromium
   ```

3. **Install Core Engine Template Modules:**
   ```bash
   cd template
   npm install
   cd ..
   ```

4. **Setup Environment Variables:**
   Create a `.env` file in the root folder containing:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

---

## Execution

Launch the agent workspace dashboard from your terminal:
```bash
streamlit run app.py
```
1. Paste a targeted web location into the prompt frame (e.g., `https://example.com`).
2. Click **Clone website** to invoke structural evaluation, framework generation, and automated live server mount on port `:3001`.
3. Use the **Modify** input to iteratively polish layout details like stickiness, animations, or styling shifts.
