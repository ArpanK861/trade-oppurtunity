# 📊 Trade Opportunities — India

A Full-Stack decoupled platform that analyzes Indian market sectors using **Groq AI** and real-time web data to generate structured, presentation-ready trade opportunity reports.

<br>
<div align="center">
  <video src="https://github.com/ArpanK861/trade-oppurtunity/raw/main/Trade%20Video.mp4" width="100%" controls></video>
</div>
<br>

---

## 🚀 Key Features

- **AI-Powered Analysis** — Integrates with Groq's high-speed inference API (Llama 3) for deep structural market reports.
- **Beautiful React Frontend** — A stunning, minimalist hero interface built with Vite, Tailwind CSS v4, and React Particles.
- **Real-Time Web Scrape** — DuckDuckGo search integration collects the absolute latest market news prior to AI synthesis.
- **Decoupled Architecture** — Completely split Backend (FastAPI) and Frontend (React/Vite) ready for microservice PaaS deployment.
- **Automated Security** — JWT Guest Authentication logic (no user signup required) and aggressive 5 req/min rate limiting via SlowAPI.
- **In-Memory Caching** — 15-minute cache to avoid duplicate expensive AI queries.

---

## 📁 Project Structure

```text
trade/
├── app/                        # FastAPI Backend
│   ├── main.py                 # Application entry and CORS configuration
│   ├── config.py               # Settings from .env and Allowed Sectors
│   ├── api/endpoints.py        # API routes (/analyze, /auth/guest)
│   ├── core/                   # Security and Rate Limiter
│   ├── services/               # DuckDuckGo search and Groq analyzer
│   └── models/                 # Pydantic validation models
├── frontend/                   # React Frontend
│   ├── src/                    # Components (Hero, ReportViewer, FloatingBackground)
│   ├── index.css               # Tailwind v4 configuration
│   └── package.json            # Node dependencies
├── tests/                      # Pytest backend test suite
├── render.yaml                 # Render.com backend deployment blueprint
├── requirements.txt            # Python dependencies
└── run.py                      # Local server launcher
```

---

## ⚡ Quick Start Local Development

### 1. Start the Backend

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Configure Environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (Get free key at: https://console.groq.com/keys)

# 3. Launch FastAPI Server
python run.py
```
*The backend will be available at `http://localhost:8000`*

### 2. Start the Frontend

Open a new terminal window:
```bash
cd frontend

# 1. Install Node modules
npm install

# 2. Launch Vite Dev Server
npm run dev
```
*The UI will be available at `http://localhost:5173`*

---

## 🌍 Production Deployment

This project is pre-configured for a **100% Free** split-stack deployment using Vercel & Render.

### Backend (Render.com)
1. Push this repository to GitHub.
2. Log into Render and create a new **Blueprint**.
3. Select your repository. Render will read `render.yaml` and auto-deploy your FastAPI backend.
4. Add your `GROQ_API_KEY` to the Render environment variables.

### Frontend (Vercel)
1. Log into Vercel and import your GitHub repository.
2. Set the `Root Directory` to `frontend/`.
3. Add an Environment Variable: `VITE_API_URL` -> *(Paste your deployed Render backend URL here)*
4. Click Deploy. Vercel will install the dependencies, build the React app, and apply the SPA routing rules found in `frontend/vercel.json`.

**Final Step:** Don't forget to take your newly minted Vercel URL and add it to `CORS_ORIGINS` in your Render backend environment variables!

---

## 🔒 Security Posture

- **Strict Validation:** All input requests are heavily sanitized and strict-matched against the `ALLOWED_SECTORS` list in `config.py` preventing Prompt Injection.
- **Markdown Sandbox:** The frontend `ReportViewer.jsx` parses the AI response carefully without `rehypeRaw`, rendering HTML-injection completely inert.
- **Stateless Tokens:** Accessing the API requires generating a short-lived JSON Web Token restricting brute-force API hammering.

---

## 📄 License
MIT
